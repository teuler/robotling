/*-----------------------------------------------------------------------
  module `blob`

  cd ~/micropython/ports/esp32
  make USER_C_MODULES=../../../modules CFLAGS_EXTRA=-DMODULE_BLOB_ENABLED=1 all
*-----------------------------------------------------------------------*/
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "stack.h"

#define BLOB_ERRC_OK       0
#define BLOB_ERRC_MEMORY  -1

#define MAX_BLOBS          5
#define MAX_BLOB_FIELDS    5
#define FILTER_SIZE        3
#define MAX_FILTERS        2
#define BYTE               unsigned char

const float filterSet[MAX_FILTERS][FILTER_SIZE][FILTER_SIZE]
  = {{{1,  1, 1}, {1,  1,  1}, {1,  1, 1}},
     {{0, -1, 0}, {-1, 5, -1}, {0, -1, 0}}};

const int xoffs[4]         = {-1, 1,  0, 0};
const int yoffs[4]         = { 0, 0, -1, 1};

typedef struct blob_struct {
  int area;
  int ID;
  float prob;
  float x, y;
} blob_struct_t;

// ----------------------------------------------------------------------------
STATIC void filter(int dx, int dy, float *pImg, int mode)
{
  int n = dx*dy;
  float avg, sum;
  float *pTmp = NULL;
  int r, dxf, dyf, x, y, j, nf, m, ix, iy;

  // Check parameters
  if((mode <= 0) || (mode > MAX_FILTERS))
    // No filter requested or invalid filter mode
    return;

  // Calculate average for edge pixels
  sum = 0;
  avg = 0;
  for(j=0; j<n; j++)
    sum += pImg[j];
  avg = sum /n;

  // Make a larger image copy for the filtering
  r = (int)trunc((FILTER_SIZE -1)/2);
  dxf = dx +r*2;
  dyf = dy +r*2;
  nf = dxf*dyf;
  pTmp = malloc(nf*sizeof(*pTmp));
  for(j=0; j<nf; j++)
    pTmp[j] = avg;
  for(x=0; x<dx; x++) {
    for(y=0; y<dy; y++) {
      pTmp[x+r +(y+r)*dx] = pImg[x +y*dx];
    }
  }
  // Apply filter ...
  for(x=0; x<dxf; x++) {
    for(y=0; y<dyf; y++) {
      if((y >= r) && (y < dyf-r) && (x >= r) && (x < dxf-r)) {
        sum = 0;
        m = 0;
        for(iy=-r; iy<r; iy++) {
          for(ix=-r; ix<r; ix++) {
            sum += pTmp[x+ix +(y+iy)*dxf] *filterSet[mode-1][ix+r][iy+r];
            if(filterSet[mode-1][ix+r][iy+r] != 0)
              m++;
          }
        }
        pImg[x-r +(y-r)*dx] = sum/m;
      }
    }
  }
  free(pTmp);
}

// ----------------------------------------------------------------------------
STATIC mp_obj_t blob_detect(mp_obj_t img_obj, mp_obj_t dxy_obj,
                            mp_obj_t params_obj)
{
    blob_struct_t blobs[MAX_BLOBS];
    int nBlobs = 0;
    float *pImg = NULL;
    float *pPrb = NULL;
    BYTE *pMsk = NULL;
    int nThres, nLeft, iBlob, nFound, i, k, m, x, y;
    float avg, sd, sum, bx, by, bp;
    mp_obj_t *temp;
    stack_t posList;

    // Extract the parameters from the micropython input objects
    int dx, dy, n, mode;
    float nsd;
    mp_obj_get_array_fixed_n(dxy_obj, 2, &temp);
    dx   = mp_obj_get_int(temp[0]);
    dy   = mp_obj_get_int(temp[1]);
    mp_obj_get_array_fixed_n(params_obj, 2, &temp);
    mode = mp_obj_get_int(temp[0]);
    nsd  = mp_obj_get_float(temp[1]);
    n    = dx*dy;
    mp_obj_get_array_fixed_n(img_obj, n, &temp);
    pImg = malloc(n*sizeof(*pImg));
    pMsk = malloc(n*sizeof(*pMsk));
    pPrb = malloc(n*sizeof(*pPrb));
    if((!pImg) || (!pMsk) || (!pPrb)) {
      // Memory error
      return mp_obj_new_int(BLOB_ERRC_MEMORY);
    }
    // Copy image data into a float array
    for(i=0; i<n; i++) {
        pImg[i] = (float)mp_obj_get_int(temp[i]);
        pMsk[i] = 0;
    }

    // Apply filter, if requested
    if(mode > 0)
      filter(dx, dy, pImg, mode);

    // Mean and sd across (filtered) image
    sum = 0;
    avg = 0;
    sd  = 0;
    for(i=0; i<n; i++) {
        sum += pImg[i];
    }
    avg = sum /n;
    for(i=0; i<n; i++) {
        sum += pow(pImg[i] -avg, 2);
    }
    sd = sqrt(sum/(n-1));

    // Mark all pixels above a threshold
    nThres = 0;
    for(i=0; i<n; i++) {
      if(pImg[i] >= avg +sd *nsd) {
        pMsk[i] = (BYTE)255;
        pPrb[i] = (pImg[i] -avg) /sd;
        nThres++;
      }
    }

    // Find blobs
    stack_create(&posList, n);
    pos_struct_t p0, p1;
    nLeft = nThres;
    iBlob = 1;
    while(nLeft > 0) {
        // As long as unassigned mask pixels are left, continue going
        // the image
        for(y=0; y<dy; y++) {
            for(x=0; x<dx; x++) {
                //printf("mask(%d)=%d\n", x +y*dx, pMsk[x +y*dx]);

                if(pMsk[x +y*dx] == 255) {
                    // Unassigned pixel found ...
                    p0.x = x;
                    p0.y = y;
                    stack_push(&posList, &p0);
                    pMsk[x +y*dx] = (BYTE)iBlob;
                    nFound = 1;
                    bx = (float)x;
                    by = (float)y;
                    bp = pPrb[x +y*dx];

                    // Find all unassigned pixels in the neighborhood of
                    // this seed pixel
                    while(stack_len(&posList) > 0) {
                        stack_pop(&posList, &p0);
                        for(k=0; k<4; k++) {
                            p1.x = p0.x +xoffs[k];
                            p1.y = p0.y +yoffs[k];
                            if((p1.x >= 0) && (p1.x < dx) &&
                               (p1.y >= 0) && (p1.y < dy) &&
                               (pMsk[p1.x +p1.y*dx] == (BYTE)255)) {
                                 // Add new position from which to explore
                                 stack_push(&posList, &p1);
                                 pMsk[p1.x +p1.y*dx] = (BYTE)iBlob;
                                 nFound++;
                                 bx += (float)p1.x;
                                 by += (float)p1.y;
                                 bp += pPrb[p1.x +p1.y*dx];
                            }
                        }
                    }
                    // Update number of unassigned pixels
                    nLeft -= nFound;

                    // Store blob size and center of gravity position
                    k = 0;
                    if(iBlob > 1) {
                        while((k < iBlob) && (blobs[k].area > nFound))
                            k++;
                        if(k < iBlob) {
                            for(m=iBlob-1; m>k; m--) {
                                blobs[m]  = blobs[m-1];
                            }
                        }
                    }
                    blobs[k].ID   = iBlob;
                    blobs[k].area = nFound;
                    blobs[k].x    = by/nFound;
                    blobs[k].y    = bx/nFound;
                    blobs[k].prob = bp/nFound;
                    iBlob++;
                    /*
                    printf("iBlob=%d nLeft=%d n=%d nThres=%d nBlob=%d\n",
                           iBlob, nLeft, n, nThres, nBlobs);
                    */
                }
            }
        }
    }
    nBlobs = iBlob-1;

    // Copy blobs into list as function result
    mp_obj_t tempL = mp_obj_new_list(0, NULL);
    for(i=0; i<nBlobs; i++) {
        mp_obj_t tempT[MAX_BLOB_FIELDS] = {
            mp_obj_new_int(blobs[i].area),
            mp_obj_new_int(blobs[i].ID),
            mp_obj_new_float(blobs[i].prob),
            mp_obj_new_float(blobs[i].x),
            mp_obj_new_float(blobs[i].y)
        };
        mp_obj_list_append(tempL, mp_obj_new_tuple(MAX_BLOB_FIELDS, tempT));
    };
    // Clean up
    free(pImg);
    free(pMsk);
    free(pPrb);
    stack_kill(&posList);

    // Return list of blobs, otherwise empty list
    return tempL;
}

// ----------------------------------------------------------------------------
// Define a Python reference to the function above
STATIC MP_DEFINE_CONST_FUN_OBJ_3(blob_detect_obj, blob_detect);

// Define all properties of the blob module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t blob_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_blob) },
    { MP_ROM_QSTR(MP_QSTR_detect), MP_ROM_PTR(&blob_detect_obj) },
};
STATIC MP_DEFINE_CONST_DICT(blob_module_globals, blob_module_globals_table);

// Define module object.  
const mp_obj_module_t blob_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&blob_module_globals,
};

// Register the module to make it available in Python
MP_REGISTER_MODULE(MP_QSTR_blob, blob_user_cmodule, MODULE_BLOB_ENABLED);

// ----------------------------------------------------------------------------
