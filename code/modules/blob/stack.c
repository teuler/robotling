/* --------------------------------------------------------------------------
   stack.c - simple implementation of a stack for `pos_struct_t` elements
   --------------------------------------------------------------------------*/
#include "stack.h"
#include <stdlib.h>

// --------------------------------------------------------------------------
void stack_create(stack_t *s, int n) {
    s->iPosNext = 0;
    s->iPosLast = 0;
    s->nPos = 0;
    s->nMax = n;
    s->pPosXY = malloc(s->nMax *sizeof(*s->pPosXY));
};

void stack_kill(stack_t *s) {
    free(s->pPosXY);
    s->pPosXY = NULL;  
    s->nPos = 0;
};

int  stack_push(stack_t *s, pos_struct_t *p) {
    if(s->pPosXY) {
        s->pPosXY[s->iPosLast].x = p->x;
        s->pPosXY[s->iPosLast].y = p->y;
        s->nPos++;
        if(s->iPosLast < s->nMax-1)
            s->iPosLast++;
        else
            s->iPosLast = 0;
    }
    return s->nPos;
};

int  stack_pop(stack_t *s, pos_struct_t *p) {
  if(s->pPosXY) {
      if(s->nPos <= 0)
          return -1;
      p->x = s->pPosXY[s->iPosNext].x;
      p->y = s->pPosXY[s->iPosNext].y;
      if(s->iPosNext < s->nMax-1)
          s->iPosNext++;
      else
          s->iPosNext = 0;
      s->nPos--;
  }
  return s->nPos;
};

int  stack_len(stack_t *s) {
    return s->nPos;
};

// ----------------------------------------------------------------------------
