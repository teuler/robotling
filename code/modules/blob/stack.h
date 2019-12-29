/* --------------------------------------------------------------------------
   stack.h - simple implementation of a stack for `pos_struct_t` elements
   --------------------------------------------------------------------------*/
typedef struct pos_struct {
  int x, y;
} pos_struct_t;

typedef struct stack {
  int iPosNext, iPosLast, nPos, nMax;
  pos_struct_t *pPosXY;
} stack_t;

void stack_create(stack_t *s, int n);
void stack_kill(stack_t *s);
int  stack_push(stack_t *s, pos_struct_t *p);
int  stack_pop(stack_t *s, pos_struct_t *p);
int  stack_len(stack_t *s);

// ----------------------------------------------------------------------------
