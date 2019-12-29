BLOB_MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(BLOB_MOD_DIR)/blob.c
SRC_USERMOD += $(BLOB_MOD_DIR)/stack.c

# We can add our module folder to include paths if needed
# This is not actually needed in this example.
CFLAGS_USERMOD += -I$(BLOB_MOD_DIR)
