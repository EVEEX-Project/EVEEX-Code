#-----------------------------------------------------------#
#															#
#						Variables							#
#															#
#-----------------------------------------------------------#

src = 	main.c \
		$(wildcard types/*.c) \
		$(wildcard lib/*.c)
obj = $(src:.c=.o)
dep = $(obj:.o=.d) # un fichier de dépendance par lib

CFLAGS = -MMD # option pour générer les fichiers .d
LDFLAGS = -lm

VAR = "Hello"

#-----------------------------------------------------------#
#															#
#					Règles de compilation					#
#															#
#-----------------------------------------------------------#

build-x86: CC = gcc
build-riscV: CC = riscv32-unknown-elf-gcc

.PHONY: build
build-x86 build-riscV: $(obj)
	$(CC) -o eveex-x86 $^ $(LDFLAGS)

-include $(dep)

# Regèle pour build les libs en fichier objet
%.o: %.c
	$(CC) $(CFLAGS) -o $@ -c $<

#-----------------------------------------------------------#
#															#
#					Règles de nettoyage						#
#															#
#-----------------------------------------------------------#
# Nettoyer les produits de make
.PHONY: clean
clean: cleanbuild cleandep
	rm -f eveex-x86

# Nettoyer les libs compilées
.PHONY: cleanbuild
cleanbuild:
	rm -f $(obj)

# Nettoyer des fichiers de dépendence
.PHONY: cleandep
cleandep:
	rm -f $(dep)
