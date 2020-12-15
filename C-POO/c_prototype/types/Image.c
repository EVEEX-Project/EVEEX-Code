#include <stdlib.h>

#define STB_IMAGE_IMPLEMENTATION
#include "../lib/stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "../lib/stb_image_write.h"

#include "Image.r"
#include "Image.h"

/**************************************************************************/
/*							  METHODES UTILES   						  */
/**************************************************************************/

static inline int str_ends_in(const char *str, const char *ends) {
    char *pos = strrchr(str, '.');
    return !strcmp(pos, ends);
}

/**************************************************************************/
/*							  CLASSE IMAGE								  */
/**************************************************************************/

/* Constructeur avec arguments */
// args : int width, int height, int channels, bool init_with_zeros
static void *Image_ctor (void *_self, va_list *app) {
    struct Image *self = super_ctor(Image(), _self, app);

    // On récupère les arguments dynamiques
    int width = va_arg(*app, int);
    int height = va_arg(*app, int);
    int channels = va_arg(*app, int);
    char init_with_zeros = va_arg(*app, int);

    size_t size = width * height * channels;

    // if we set the initialisation with zeros
    if(init_with_zeros == 1) {
        self->data = (uint8_t *) calloc(size, 1);
    } else {
        self->data = (uint8_t *) malloc(size);
    }

    // if the data is null there is not enough space...
    if (!self->data) {
        perror("Error while initializing image");
        exit(EXIT_FAILURE);
    }

    // else we set the rest of the properties
    self->width = width;
    self->height = height;
    self->size = size;
    self->channels = channels;
    self->allocationType = SELF_ALLOCATED;

    return self;
}

/* Destructeur */
static void *Image_dtor (void *_self) {
    struct Image *self = cast(Image(), _self);
    // rien d'autre à libérer on retourne la référence à l'objet
    // pour être libéré avec free()

    if(self->allocationType != NO_ALLOCATION && self->data != NULL) {
        // if the image was loaded and not created
        if(self->allocationType == STB_ALLOCATED) {
            // then we unload the image
            stbi_image_free(self->data);
        } else {
            // else we only free the data
            free(self->data);
        }
        // then it's just a matter of resetting everything
        self->data = NULL;
        self->width = 0;
        self->height = 0;
        self->size = 0;
        self->allocationType = NO_ALLOCATION;
    }

    // then we free the structure
    return self;
}

/* Méthode de classe */
static void Image_save(const void *_self, const char *file_name) {
    const struct Image *self = _self;

    // Check if the file name ends in one of the .jpg/.JPG/.jpeg/.JPEG or .png/.PNG
    if(str_ends_in(file_name, ".jpg")
       || str_ends_in(file_name, ".JPG")
       || str_ends_in(file_name, ".jpeg")
       || str_ends_in(file_name, ".JPEG")) {
        // then we write the image
        stbi_write_jpg(file_name, self->width, self->height, self->channels, self->data, self->width * self->channels);
    }
    else if(str_ends_in(file_name, ".png")
            || str_ends_in(file_name, ".PNG")) {
        // then we write the image
        stbi_write_png(file_name, self->width, self->height, self->channels, self->data, self->width * self->channels);
    } else {
        // the format is not recognized
        char message[100];
        sprintf(message, "Bad extension (or no extension at all) for the filename : '%s'", file_name);
        perror(message);
        exit(EXIT_FAILURE);
    }
}

static const struct Image *Image_toGray(const void *_self) {
    const struct Image *self = _self;

    // check for a valid image
    if(self->allocationType == NO_ALLOCATION || self->channels < 3) {
        perror("The input image must have at least 3 channels.");
        exit(EXIT_FAILURE);
    }

    // setting the correct number of channels
    int channels = self->channels == 4 ? 2 : 1;
    // creating the destination image
    void *_copy = new(Image(), self->width, self->height, channels, 0);
    const struct Image *copy = _copy;

    // values of each RGB pixel
    uint8_t p0, p1, p2;
    // iteration over the pixels of the image
    for(uint8_t *p = self->data, *pg = copy->data; p != self->data + self->size; p += self->channels, pg += copy->channels) {
        // updating the pixels value
        p0 = *p, p1 = *(p + 1), p2 = *(p + 2);
        // updating the target pixel
        *pg = (uint8_t)((p0 + p1 + p2)/3.0);
        // if there was transparency
        if(self->channels == 4) {
            // update the transparency pixel
            *(pg + 1) = *(p + 3);
        }
    }

    return copy;
}

static const struct Image *Image_toSepia(const void *_self) {
    const struct Image *self = _self;

    // check for a valid image
    if(self->allocationType == NO_ALLOCATION || self->channels < 3) {
        perror("The input image must have at least 3 channels.");
        exit(EXIT_FAILURE);
    }

    // setting the correct number of channels
    int channels = self->channels == 4 ? 2 : 1;
    // creating the destination image
    void *_copy = new(Image(), self->width, self->height, channels, 0);
    const struct Image *copy = _copy;

    // values of each RGB pixel
    uint8_t p0, p1, p2;
    // iteration over the pixels of the image
    for(uint8_t *p = self->data, *pg = copy->data; p != self->data + self->size; p += self->channels, pg += copy->channels) {
        *pg       = (uint8_t)fmin(0.393 * *p + 0.769 * *(p + 1) + 0.189 * *(p + 2), 255.0);         // red
        *(pg + 1) = (uint8_t)fmin(0.349 * *p + 0.686 * *(p + 1) + 0.168 * *(p + 2), 255.0);         // green
        *(pg + 2) = (uint8_t)fmin(0.272 * *p + 0.534 * *(p + 1) + 0.131 * *(p + 2), 255.0);         // blue
        // if there was transparency
        if(self->channels == 4) {
            // update the transparency pixel
            *(pg + 1) = *(p + 3);
        }
    }

    return copy;
}

/* Override d'une méthode de classe parente */
static void Image_puto(const void * _self, FILE * fp) {
    const struct Image *self = _self;
    fprintf(fp, "Image: (height, width): (%d, %d), Channels: %d\n", self->height, self->width, self->channels);
}

/**************************************************************************/
/*							MÉTACLASSE IMAGECLASS						  */
/**************************************************************************/

/* Méthode statique */
const struct Image *loadImg(const char *file_name) {
    struct Image *self = new(Image(), 0, 0, 0, 0);

    self->data = stbi_load(file_name, &self->width, &self->height, &self->channels, 0);

    // if the data is null there was a problem during the loading
    if(self->data == NULL) {
        perror("Error while loading image ...");
        exit(EXIT_FAILURE);
    }

    // else we load the rest of the infos
    self->size = self->width * self->height * self->channels;
    self->allocationType = STB_ALLOCATED;

    return self;
}

/* Méthode de classe */
void saveImg(const void *_self, const char *fileName) {
    const struct ImageClass *class = classOf(_self);

    assert(class->saveImg); // on vérifie que l'objet possède bien la fonction
    class->saveImg(_self, fileName); // on appelle la fonction de l'objet
}

const struct Image *toGray(const void *_self) {
    const struct ImageClass *class = classOf(_self);

    assert(class->toGray); // on vérifie que l'objet possède bien la fonction
    class->toGray(_self); // on appelle la fonction de l'objet
}

const struct Image *toSepia(const void *_self) {
    const struct ImageClass *class = classOf(_self);

    assert(class->toSepia); // on vérifie que l'objet possède bien la fonction
    class->toSepia(_self); // on appelle la fonction de l'objet
}

/* Constructeur */
static void * ImageClass_ctor (void * _self, va_list * app) {
    // on appelle le constructeur du parent (appel en chaîne jusqu'à objet)
    struct ImageClass * self = super_ctor(ImageClass(), _self, app);
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
        if (selector == (voidf) saveImg)
            *(voidf *) &self->saveImg = method;
        if (selector == (voidf) toGray)
            *(voidf *) &self->toGray = method;
        if (selector == (voidf) toSepia)
            *(voidf *) &self->toSepia = method;
    }
#ifdef va_copy
    va_end(ap);
#endif

    return self;
}

/**************************************************************************/
/*				   	   INITIALISATION IMAGE, IMAGECLASS					  */
/**************************************************************************/
static const void *_Image, *_ImageClass; // références internes

// référence externe dans le projet
const void *const ImageClass(void) {
    return _ImageClass ?
           _ImageClass : (_ImageClass = new(Class(), "ImageClass",
                                            Class(), sizeof(struct ImageClass),
                                            ctor, ImageClass_ctor,	// constructeur de classe
                                            (void *) 0));
}

// référence externe dans le projet
const void *const Image(void) {
    return _Image ?
           _Image : (_Image = new(ImageClass(), "Image",
                                  Object(), sizeof(struct Image),
                                  ctor, Image_ctor,		// contructeur de classe
                                  dtor, Image_dtor,		// méthodes de classe (obligatoire)
                                  puto, Image_puto,
                                  saveImg, Image_save,
                                  toGray, Image_toGray,
                                  toSepia, Image_toSepia,
                                  (void *) 0));
}