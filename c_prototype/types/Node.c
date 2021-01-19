#include <malloc.h>

#include "Node.r"
#include "Node.h"

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

static void Node_puto(void *_self, FILE *fp) {
    struct Node *self = cast(Node(), _self);
    fprintf(fp, "Node: frequency=%ld, value=", self->frequency);
    puto(self->value, fp);
}

static void *Node_clone(const void *_self) {
    const struct Node *self = _self;
    return new(Node(), self->frequency, self->value);
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