/* --------------------------------------------------------------------------
   stack.c - simple implementation of a stack for `pos_struct_t` elements
   --------------------------------------------------------------------------*/
#include "stack.h"
#include <stdlib.h>

// --------------------------------------------------------------------------
void stack_create(stack_t *s, int n) {
    s->iPosLast = 0;
    s->nMax = n;
    s->nPos = 0;
    s->pPosXY = malloc(s->nMax *sizeof(*s->pPosXY));
};

void stack_kill(stack_t *s) {
    free(s->pPosXY);
    s->pPosXY = NULL;
    s->nPos = 0;
};

int stack_push(stack_t *s, pos_struct_t *p) {
    if((s->pPosXY) && (s->nPos < s->nMax)) {
        s->pPosXY[s->iPosLast].x = p->x;
        s->pPosXY[s->iPosLast].y = p->y;
        if(s->nPos > 0)
            s->iPosLast++;
        s->nPos++;
        return s->nPos;
    }
    else
        return -1;
};

int stack_top(stack_t *s, pos_struct_t *p) {
    if((s->pPosXY) && (s->nPos > 0)) {
        p->x = s->pPosXY[s->iPosLast].x;
        p->y = s->pPosXY[s->iPosLast].y;
        return s->iPosLast;
    }
    else
        return -1;
};

void stack_pop(stack_t *s) {
    if((s->pPosXY) && (s->nPos > 0)) {
        s->nPos--;
        if(s->iPosLast > 0)
            s->iPosLast--;
    }
};

int  stack_len(stack_t *s) {
    return s->nPos;
};

// ----------------------------------------------------------------------------
