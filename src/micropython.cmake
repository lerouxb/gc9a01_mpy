set(MCUFONT_DIR $ENV{MCUFONT_DIR})
if (NOT MCUFONT_DIR)
    set(MCUFONT_DIR /home/lerouxb/src/mcufont)
endif()

set(DECODER_DIR ${MCUFONT_DIR}/decoder)
set(FONTS_DIR ${MCUFONT_DIR}/fonts)

message(MCUFONT_DIR="${MCUFONT_DIR}")
message(DECODER_DIR="${DECODER_DIR}")
message(FONTS_DIR="${FONTS_DIR}")

# Create an INTERFACE library for our C module.
add_library(usermod_gc9a01 INTERFACE)

target_sources(usermod_gc9a01 INTERFACE
    # Add our source files to the lib
    ${CMAKE_CURRENT_LIST_DIR}/gc9a01.c
    ${CMAKE_CURRENT_LIST_DIR}/mpfile.c
    ${CMAKE_CURRENT_LIST_DIR}/tjpgd565.c
    # and mcufont's decoder's source files
    ${DECODER_DIR}/mf_encoding.c
    ${DECODER_DIR}/mf_font.c
    ${DECODER_DIR}/mf_justify.c
    ${DECODER_DIR}/mf_kerning.c
    ${DECODER_DIR}/mf_rlefont.c
    ${DECODER_DIR}/mf_bwfont.c
    ${DECODER_DIR}/mf_scaledfont.c
    ${DECODER_DIR}/mf_wordwrap.c
)

target_include_directories(usermod_gc9a01 INTERFACE
    # Add the current directory as an include directory.
    ${CMAKE_CURRENT_LIST_DIR}
    # and MCUFONT's decoder and fonts
    ${DECODER_DIR}
    ${FONTS_DIR}

)
target_compile_definitions(usermod_gc9a01 INTERFACE
    MODULE_GC9A01_ENABLED=1
)

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE usermod_gc9a01)
