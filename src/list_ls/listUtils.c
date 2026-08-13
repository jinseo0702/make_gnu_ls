#include "../../include/ls_list.h"
#include <string.h>
#include <time.h>
#include <unistd.h>

void free_ls_list(t_list_ls **list) {
    if (list && *list) {
        free(*list);
        *list = NULL;
    }
}

void free_long_format(t_logformat **long_format) {
    t_logformat *temp = *long_format;
    if (long_format && *long_format) {
        ft_freenull(&temp->authority);
        ft_freenull(&temp->hardlink);
        ft_freenull(&temp->owner);
        ft_freenull(&temp->group);
        ft_freenull(&temp->size);
        ft_freenull(&temp->date);
        ft_freenull(&temp->name);
        free(*long_format);
        *long_format = NULL;
    }
}

t_list_ls *init_ls_list() {
    t_list_ls *return_value = malloc(sizeof(t_list_ls));
    if (return_value == NULL) return NULL; //굳이 사용해야 할까?
    ft_memset(return_value, 0, sizeof(t_list_ls));
    return return_value;
}

unsigned int cnt_ls_list(t_list_ls **head) {
    unsigned int cnt = 0;
    t_list_ls *temp = *head;
    while (temp) {
        cnt++;
        temp = temp->next;
    }
    return cnt;
}

/*
하드 링크 : 오른쪽
소유자 : 외쪽
그룹 : 왼쪽
사이즈 : 오른쪽
일 : 오른쪽
시간 or 년도 : 오른쪽
falg : flag >= 0 ; flag <= 4
*/
unsigned int max_len_str_in_longform(t_list_ls **head, int flag) {
    unsigned int val = 0;
    t_list_ls *temp = *head;
    char *ptr;

    while (temp) {
        switch (flag) {
            case 0:
                ptr = temp->long_format->hardlink;
            break;
            case 1:
                ptr = temp->long_format->owner;
            break;
            case 2:
                ptr = temp->long_format->group;
            break;
            case 3:
                ptr = temp->long_format->size;
            break;
            case 4:
                ptr = temp->long_format->date;
            break;
        }
        if (ft_strlen(ptr) > val) val = ft_strlen(ptr);
        temp = temp->next;
    }
    return val;
}

void ls_list_pushChild(t_list_ls **head, t_list_ls *child) {
    t_list_ls *temp = *head;
    temp->child = child;
}

void free_all_ls_list(t_list_ls **head){
    t_list_ls *temp = *head;

    while (temp) {
        if (temp->child != NULL) free_all_ls_list(&temp->child);
        if (temp->name != NULL) ft_freenull(&temp->name);
        if (temp->path != NULL) ft_freenull(&temp->path);
        if (temp->long_format != NULL) free_long_format(&temp->long_format);
        temp = temp->next;
        free_ls_list(head);
        *head = temp;
    }
}

void ls_list_pushBack(t_list_ls **head, t_list_ls *next) {
    t_list_ls *temp = *head;
    while (temp) {
        if (temp->next == NULL) {
            temp->next = next;
            break;
        }
        temp = temp->next;
    }
}

void ls_list_remove(t_list_ls **head, const unsigned char c) {
    t_list_ls **pp= head;
    t_list_ls *cur;
    while (*pp) {
        cur = *pp;
        if (cur->name && (unsigned char)cur->name[0] == c) {
            *pp = cur->next;
            if (cur->name != NULL) ft_freenull(&cur->name);
            if (cur->path != NULL) ft_freenull(&cur->path);
            free_ls_list(&cur);
            continue;
        }
        pp = &((*pp)->next);
    }
}

void sort_list(t_list_ls **head, int (*cmp)(const char *, const char *, size_t)) {
    int swapped;
    t_list_ls *cur;
    t_list_ls *next;
    t_list_ls **pp;
    size_t len_cur;
    size_t len_next;
    size_t len;

    do {
        swapped = 0;
        pp = head;
        while (*pp && (*pp)->next) {
            cur = *pp;
            next = cur->next;
            len_cur = ft_strlen(cur->name);
            len_next = ft_strlen(next->name);
            len = len_cur > len_next ? len_cur : len_next;
            if (cmp(cur->name, next->name, len) > 0) {
                cur->next = next->next;
                next->next = cur;
                *pp = next;
                swapped = 1;
            }
            pp = &((*pp)->next);
        }
    }while (swapped);
}

void sort_reverse_list(t_list_ls **head, int (*cmp)(const char *, const char *, size_t)) {
    int swapped;
    t_list_ls *cur;
    t_list_ls *next;
    t_list_ls **pp;
    size_t len_cur;
    size_t len_next;
    size_t len;

    do {
        swapped = 0;
        pp = head;
        while (*pp && (*pp)->next) {
            cur = *pp;
            next = cur->next;
            len_cur = ft_strlen(cur->name);
            len_next = ft_strlen(next->name);
            len = len_cur > len_next ? len_cur : len_next;
            if (cmp(cur->name, next->name, len) < 0) {
                cur->next = next->next;
                next->next = cur;
                *pp = next;
                swapped = 1;
            }
            pp = &((*pp)->next);
        }
    }while (swapped);
}

void time_sort_list(t_list_ls **head) {
    int swapped;
    t_list_ls *cur;
    t_list_ls *next;
    t_list_ls **pp;
    time_t cur_tst = 0;
    time_t next_tst = 0;
    time_t diffs = 0;
    long cur_nst = 0;
    long next_nst = 0;
    long diffn = 0;

    do {
        swapped = 0;
        pp = head;
        while (*pp && (*pp)->next) {
            cur = *pp;
            next = cur->next;
            cur_tst = cur->st_mtim.tv_sec;
            next_tst = next->st_mtim.tv_sec;
            diffs = cur_tst - next_tst;
            if (diffs == 0) {
                cur_nst = cur->st_mtim.tv_nsec;
                next_nst = next->st_mtim.tv_nsec;
                diffn = cur_nst - next_nst;
                diffs = diffn;
            }
            if (diffs < 0) {
                cur->next = next->next;
                next->next = cur;
                *pp = next;
                swapped = 1;
            }
            pp = &((*pp)->next);
        }
    }while (swapped);
}

void time_sort_reverse_list(t_list_ls **head) {
    int swapped;
    t_list_ls *cur;
    t_list_ls *next;
    t_list_ls **pp;
    time_t cur_tst = 0;
    time_t next_tst = 0;
    time_t diffs = 0;
    long cur_nst = 0;
    long next_nst = 0;
    long diffn = 0;

    do {
        swapped = 0;
        pp = head;
        while (*pp && (*pp)->next) {
            cur = *pp;
            next = cur->next;
            cur_tst = cur->st_mtim.tv_sec;
            next_tst = next->st_mtim.tv_sec;
            diffs = cur_tst - next_tst;
            if (diffs == 0) {
                cur_nst = cur->st_mtim.tv_nsec;
                next_nst = next->st_mtim.tv_nsec;
                diffn = cur_nst - next_nst;
                diffs = diffn;
            }
            if (diffs > 0) {
                cur->next = next->next;
                next->next = cur;
                *pp = next;
                swapped = 1;
            }
            pp = &((*pp)->next);
        }
    }while (swapped);
}