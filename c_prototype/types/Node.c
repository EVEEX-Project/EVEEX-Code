#include <malloc.h>
#include <string.h>

#include "Node.r"
#include "Node.h"
#include "List.h"
#include "Native.h"
#include "Native.r"

/**************************************************************************/
/*							  CLASSE NODE   							  */
/**************************************************************************/

/* Constructeur avec arguments */
static void *Node_ctor (void *_self, va_list *app) {
    struct Node *self = super_ctor(Node(), _self, app);

    // On récupère les arguments dynamiques
    self->frequency = va_arg(*app, unsigned long);
    self->value = clone(va_arg(*app, struct Object *));
    self->left = NULL;
    self->right = NULL;

    return self;
}

/* Destructeur */
static void *Node_dtor (void *_self) {
    struct Node *self = cast(Node(), _self);
    self->left = NULL;
    self->right = NULL;

    if (self->value)
        delete(self->value);

    return self;
}

static char* getNodeValue(void *_self) {
    struct Node *self = cast(Node(), _self);

    char *res = malloc(count(self->value) * sizeof(char) * 2);
    for (int i = 0; i < count(self->value); i++) {
        struct Native *value = cast(Native(), lookAt(self->value, i));
        res[2*i] = *((char *) value->value);
        res[2*i+1] = ',';
    }
    res[count(self->value)*2-1] = '\0';
    return res;
}

static void Node_puto(void *_self, FILE *fp) {
    struct Node *self = cast(Node(), _self);
    char *value = getNodeValue(self);
    fprintf(fp, "Node: frequency=%ld, value=%s\n", self->frequency, value);
    free(value);
}

static void *Node_clone(const void *_self) {
    const struct Node *self = _self;
    struct Node *cloneObj;

    // si on est au bout d'une branche
    if (!self->right && !self->left) {
        struct Native *val = cast(Native(), lookAt(self->value, 0));
        char *newSym = malloc(strlen(val->value) + 1);
        strcpy(newSym, val->value);
        struct List *newVal = new(List());
        addLast(newVal, new(Native(), newSym, strlen(val->value) + 1));
        cloneObj = new(Node(), self->frequency, newVal);
    } else {
        cloneObj = new(Node(), self->frequency, self->value);
        if (self->right)
            cloneObj->right = clone(self->right);
        if (self->left)
            cloneObj->left = clone(self->left);
    }
    return cloneObj;
}

/* Méthodes statiques */
struct Node *copyNode(const void *_self) {
    const struct Node *self = _self;

    return new(Node(), self->frequency, self->value);
}

/**************************************************************************/
/*							MÉTACLASSE NODECLASS    					  */
/**************************************************************************/

/* Constructeur */
static void * NodeClass_ctor (void * _self, va_list * app) {
    // on appelle le constructeur du parent (appel en chaîne jusqu'à objet)
    struct NodeClass * self = super_ctor(NodeClass(), _self, app);
    typedef void (*voidf) ();
    voidf selector;
#ifdef va_copy
    va_list ap; va_copy(ap, *app);
#else
    va_list ap = *app;
#endif

    while ((selector = va_arg(ap, voidf))) {
        voidf method = va_arg(ap, voidf);

        // on ajoute ici les méthodes de classe
        // 1 if par méthode
    }
#ifdef va_copy
    va_end(ap);
#endif

    return self;
}

/**************************************************************************/
/*				  INITIALISATION BITSTREAM,BITSTREAMCLASS   			  */
/**************************************************************************/
static const void *_Node, *_NodeClass; // références internes

// référence externe dans le projet
const void *const NodeClass(void) {
    return _NodeClass ?
           _NodeClass : (_NodeClass = new(Class(), "NodeClass",
                                        Class(), sizeof(struct NodeClass),
                                        ctor, NodeClass_ctor,	// constructeur de classe
                                        (void *) 0));
}

// référence externe dans le projet
const void *const Node(void) {
    return _Node ?
           _Node : (_Node = new(NodeClass(), "Node",
                                          Object(), sizeof(struct Node),
                                          ctor, Node_ctor,		// contructeur de classe
                                          dtor, Node_dtor,		// méthodes de classe (obligatoire)
                                          puto, Node_puto,
                                          clone, Node_clone,
                                          (void *) 0));
}