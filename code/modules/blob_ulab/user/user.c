
/*
 * This file is part of the micropython-ulab project,
 *
 * https://github.com/v923z/micropython-ulab
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2020 Zoltán Vörös
*/

#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "py/obj.h"
#include "py/runtime.h"
#include "py/misc.h"
#include "user.h"
#include "stack.h"

#if ULAB_USER_MODULE

//| """This module should hold arbitrary user-defined functions."""
//|
// ----------------------------------------------------------------------------
#define BLOB_ERRC_OK       0
#define BLOB_ERRC_MEMORY  -1

#define MAX_BLOBS          5
#define MAX_BLOB_FIELDS    5
/*
#define FILTER_SIZE        3
#define MAX_FILTERS        2
*/
/*
#define BYTE               unsigned char
*/
/*
const float filterSet[MAX_FILTERS][FILTER_SIZE][FILTER_SIZE]
  = {{{1,  1, 1}, {1,  1,  1}, {1,  1, 1}},
     {{0, -1, 0}, {-1, 5, -1}, {0, -1, 0}}};
*/
const int xoffs[4]         = {-1, 1,  0, 0};
const int yoffs[4]         = { 0, 0, -1, 1};

typedef struct blob_struct {
  int area;
  int ID;
  mp_float_t prob, x, y;
} blob_struct_t;

// ----------------------------------------------------------------------------
static mp_obj_t user_spatial_filter(mp_obj_t img_obj, mp_obj_t kernel_obj,
                                    mp_obj_t dxy_obj)
{
  if((!mp_obj_is_type(img_obj, &ulab_ndarray_type)) ||
     (!mp_obj_is_type(kernel_obj, &ulab_ndarray_type))) {
     mp_raise_TypeError(translate("`spatial_filter` requires ndarray"));
  }
  mp_float_t avg, sum;
  int padd, j, dxf, dyf, nf, x, y, ix, iy, x2, y2, dk;

  // Extract the parameters from the micropython input objects
  ndarray_obj_t *img_arr = MP_OBJ_TO_PTR(img_obj);
  mp_float_t *img_items = (mp_float_t *)img_arr->array->items;
  ndarray_obj_t *knl_arr = MP_OBJ_TO_PTR(kernel_obj);
  if((knl_arr->m != knl_arr->n) || (knl_arr->m % 2 == 0) || (knl_arr->m <= 1)) {
    mp_raise_TypeError(translate("`kernel` must be square matrix"));
  }
  mp_float_t *knl_items = (mp_float_t *)knl_arr->array->items;
  mp_obj_t *temp;
  mp_obj_get_array_fixed_n(dxy_obj, 2, &temp);
  int dx = mp_obj_get_int(temp[0]);
  int dy = mp_obj_get_int(temp[1]);
  int n = dx*dy;
  int img_m = img_arr->m;
  int img_n = img_arr->n;
  if(img_m *img_n != n) {
    mp_raise_TypeError(translate("`img` size is inconsistent with shape in `dxy`"));
  }

  // Calculate average for edge pixels
  sum = 0;
  avg = 0;
  for(j=0; j<n; j++)
    sum += img_items[j];
  avg = sum /n;

  // Make a padded image copy for the filtering
  dk = knl_arr->m;
  padd = (int)trunc(dk /2);
  dxf = dx +padd*2;
  dyf = dy +padd*2;
  nf = dxf*dyf;
  ndarray_obj_t *imgp_arr = create_new_ndarray(dxf, dyf, NDARRAY_FLOAT);
  mp_float_t *imgp_items = (mp_float_t *)imgp_arr->array->items;

  // ... fill the borders with the mean and the centre with the image
  for(j=0; j<nf; j++)
    imgp_items[j] = avg;
  for(x=0; x<dx; x++) {
    for(y=0; y<dy; y++) {
      imgp_items[x+padd +(y+padd)*dxf] = img_items[x +y*dx];
    }
  }
  // Make image for filtered result
  ndarray_obj_t *imgf_arr = create_new_ndarray(img_m, img_n, NDARRAY_FLOAT);
  mp_float_t *imgf_items = (mp_float_t *)imgf_arr->array->items;

  // Apply filter ...
  for(x=0; x<dx; x++) {
    for(y=0; y<dy; y++) {
      sum = 0;
      for(ix=-padd; ix<=padd; ix++) {
        for(iy=-padd; iy<=padd; iy++) {
          x2 = x +padd +ix;
          y2 = y +padd +iy;
          sum += imgp_items[x2 +y2*dxf] *knl_items[ix +padd +(iy +padd)*dk];
        }
      }
      imgf_items[x +y*dx] = sum;
    }
  }
  return imgf_arr;
}

// ----------------------------------------------------------------------------
static mp_obj_t user_blobs(mp_obj_t img_obj, mp_obj_t dxy_obj,
                           mp_obj_t nsd_obj)
{
    /* Detect continues area(s) ("blobs") with pixels above a certain
       threshold in an image. `img` contains the flattened image (1D),
       `dxy` image width and height, and `nsd` a factor to calculate the
       threshold from image mean and standard deviation:
         thres = avg +sd *nsd
    */
    // TODO: More type checking
    if(!mp_obj_is_type(img_obj, &ulab_ndarray_type)) {
       mp_raise_TypeError(translate("`user_blobs` takes an ndarray image"));
    }
    int nThres, nLeft, iBlob, nFound, i, k, m, x, y, dx, dy, n;
    mp_float_t avg, sd, sum, bx, by, bp, thres, nsd;
    stack_t posList;
    mp_obj_t *temp;

    // Initialize blob array
    int nBlobs = 0;
    blob_struct_t blobs[MAX_BLOBS];
    memset(blobs, 0, sizeof(blobs));

    // Extract the parameters from the micropython input objects
    ndarray_obj_t *img_arr = MP_OBJ_TO_PTR(img_obj);
    mp_float_t *img_items = (mp_float_t *)img_arr->array->items;
    mp_obj_get_array_fixed_n(dxy_obj, 2, &temp);
    dx = mp_obj_get_int(temp[0]);
    dy = mp_obj_get_int(temp[1]);
    nsd = mp_obj_get_float(nsd_obj);
    n = dx*dy;

    // Create other arrays and zero them
    ndarray_obj_t *prb_arr = create_new_ndarray(1, n, NDARRAY_FLOAT);
    mp_float_t *prb_items = (mp_float_t *)prb_arr->array->items;
    ndarray_obj_t *msk_arr = create_new_ndarray(1, n, NDARRAY_UINT8);
    uint8_t *msk_items = (uint8_t *)msk_arr->array->items;
    for(size_t i=0; i<n; i++) {
        prb_items[i] = 0;
        msk_items[i] = 0;
    }

    // Calculate mean and sd across (filtered) image to determine threshold
    sum = 0;
    avg = 0;
    sd  = 0;
    for(i=0; i<n; i++) {
        sum += img_items[i];
    }
    avg = sum /n;
    sum = 0;
    for(i=0; i<n; i++) {
        sum += pow(img_items[i] -avg, 2);
    }
    sd = (float)sqrt(sum/(n-1));
    thres = avg +sd *nsd;

    // Mark all pixels above a threshold
    nThres = 0;
    for(i=0; i<n; i++) {
      if(img_items[i] >= thres) {
        msk_items[i] = 255;
        prb_items[i] = (img_items[i] -avg) /sd;
        nThres++;
      }
    }

    // Find blobs
    stack_create(&posList, n);
    pos_struct_t p0, p1;
    nLeft = nThres;
    iBlob = 0;
    while((nLeft > 0) && (iBlob < MAX_BLOBS)) {
        // As long as unassigned mask pixels are left, continue going
        // the image
        for(y=0; y<dy; y++) {
            for(x=0; x<dx; x++) {
                if(msk_items[x +y*dx] == 255) {
                    // Unassigned pixel found ...
                    p0.x = x;
                    p0.y = y;
                    stack_push(&posList, &p0);
                    msk_items[x +y*dx] = iBlob;
                    nFound = 1;
                    bx = (mp_float_t)x;
                    by = (mp_float_t)y;
                    bp = prb_items[x +y*dx];

                    // Find all unassigned pixels in the neighborhood of
                    // this seed pixel
                    while(stack_len(&posList) > 0) {
                        stack_top(&posList, &p0);
                        stack_pop(&posList);
                        for(k=0; k<4; k++) {
                            p1.x = p0.x +xoffs[k];
                            p1.y = p0.y +yoffs[k];
                            if((p1.x >= 0) && (p1.x < dx) &&
                               (p1.y >= 0) && (p1.y < dy) &&
                               (msk_items[p1.x +p1.y*dx] == 255)) {
                                 // Add new position from which to explore
                                 stack_push(&posList, &p1);
                                 msk_items[p1.x +p1.y*dx] = iBlob;
                                 nFound++;
                                 bx += p1.x;
                                 by += p1.y;
                                 bp += prb_items[p1.x +p1.y*dx];
                            }
                        }
                    }
                    // Update number of unassigned pixels
                    nLeft -= nFound;

                    // Store blob size and center of gravity position
                    k = 0;
                    if(iBlob > 0) {
                        while((k < iBlob) && (blobs[k].area > nFound))
                            k++;
                        if(k < iBlob) {
                            for(m=iBlob-1; m>k; m--) {
                                blobs[m] = blobs[m-1];
                            }
                        }
                    }
                    blobs[k].ID   = iBlob;
                    blobs[k].area = nFound;
                    blobs[k].x    = by/nFound;
                    blobs[k].y    = bx/nFound;
                    blobs[k].prob = bp/nFound;
                    iBlob++;
                }
            }
        }
    }
    nBlobs = iBlob;

    // Copy blobs into list as function result
    mp_obj_t tempL = mp_obj_new_list(0, NULL);
    for(i=0; i<nBlobs; i++) {
        if(blobs[i].area > 0) {
            mp_obj_t tempT[MAX_BLOB_FIELDS] = {
                mp_obj_new_int(blobs[i].area),
                mp_obj_new_int(blobs[i].ID),
                mp_obj_new_float(blobs[i].prob),
                mp_obj_new_float(blobs[i].x),
                mp_obj_new_float(blobs[i].y)
            };
            mp_obj_list_append(tempL, mp_obj_new_tuple(MAX_BLOB_FIELDS, tempT));
        };
    };
    // Clean up
    stack_kill(&posList);

    // Return list of blobs, otherwise empty list
    return tempL;
}

// ----------------------------------------------------------------------------
MP_DEFINE_CONST_FUN_OBJ_3(user_blobs_obj, user_blobs);
MP_DEFINE_CONST_FUN_OBJ_3(user_spatial_filter_obj, user_spatial_filter);

STATIC const mp_rom_map_elem_t ulab_user_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_user) },
	  { MP_OBJ_NEW_QSTR(MP_QSTR_blobs), (mp_obj_t)&user_blobs_obj },
    { MP_OBJ_NEW_QSTR(MP_QSTR_spatial_filter), (mp_obj_t)&user_spatial_filter_obj },
};

STATIC MP_DEFINE_CONST_DICT(mp_module_ulab_user_globals,
                            ulab_user_globals_table);

mp_obj_module_t ulab_user_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_ulab_user_globals,
};

#endif
