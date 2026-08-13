#ifndef LS_LIST_H
#define LS_LIST_H

#include <sys/types.h>
#include <stdlib.h>
#include <dirent.h>
#include "../libft/libft.h"
#include "./dirStream.h"


typedef struct dirent dirent;
typedef struct s_longformat t_logformat;


typedef struct s_list_ls {
    DIR *openDir;
    char *path;
    dirent readDirPtr;
    char *name;
    t_logformat *long_format;
    mode_t st_mode;
    nlink_t st_nlink;
    uid_t st_uid;
    gid_t st_gid;
    off_t st_size;
    blkcnt_t st_blocks;
    struct timespec st_mtim;
    long ErrorNum;

    struct s_list_ls *next;
    struct s_list_ls *child;
} t_list_ls ;

t_list_ls *init_ls_list();
unsigned int cnt_ls_list(t_list_ls **head);
void ls_list_pushBack(t_list_ls **head, t_list_ls *next);
void ls_list_pushChild(t_list_ls **head, t_list_ls *child);
unsigned int max_len_str_in_longform(t_list_ls **head, int flag);
void free_all_ls_list(t_list_ls **head);
void  free_ls_list(t_list_ls **list);
void free_long_format(t_logformat **long_format);
void ls_list_remove(t_list_ls **head, const unsigned char c);
void sort_list(t_list_ls **head, int (*cmp)(const char *, const char *, size_t));
void sort_reverse_list(t_list_ls **head, int (*cmp)(const char *, const char *, size_t));
void time_sort_list(t_list_ls **head);
void time_sort_reverse_list(t_list_ls **head);


#endif