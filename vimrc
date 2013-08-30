" An example for a vimrc file.
"
" Maintainer:	Bram Moolenaar <Bram@vim.org>
" Last change:	2002 Sep 19
"
" To use it, copy it to
"     for Unix and OS/2:  ~/.vimrc
"	      for Amiga:  s:.vimrc
"  for MS-DOS and Win32:  $VIM\_vimrc
"	    for OpenVMS:  sys$login:.vimrc

" When started as "evim", evim.vim will already have done these settings.
if v:progname =~? "evim"
  finish
endif

" Use Vim settings, rather then Vi settings (much better!).
" This must be first, because it changes other options as a side effect.
set nocompatible

" allow backspacing over everything in insert mode
set backspace=indent,eol,start

"if has("vms")
  set nobackup		" do not keep a backup file, use versions instead
"else
  "set backup		" keep a backup file
"endif
set history=50		" keep 50 lines of command line history
set ruler		" show the cursor position all the time
set showcmd		" display incomplete commands
set incsearch		" do incremental searching

" For Win32 GUI: remove 't' flag from 'guioptions': no tearoff menu entries
" let &guioptions = substitute(&guioptions, "t", "", "g")

" Don't use Ex mode, use Q for formatting
map Q gq

" This is an alternative that also works in block mode, but the deleted
" text is lost and it only works for putting the current register.
"vnoremap p "_dp

" Switch syntax highlighting on, when the terminal has colors
" Also switch on highlighting the last used search pattern.
if &t_Co > 2 || has("gui_running")
  syntax on
  set hlsearch
endif

" Only do this part when compiled with support for autocommands.
if has("autocmd")

  " Enable file type detection.
  " Use the default filetype settings, so that mail gets 'tw' set to 72,
  " 'cindent' is on in C files, etc.
  " Also load indent files, to automatically do language-dependent indenting.
  filetype plugin indent on

  " Put these in an autocmd group, so that we can delete them easily.
  augroup vimrcEx
  au!

  " For all text files set 'textwidth' to 78 characters.
  autocmd FileType text setlocal textwidth=78

  " When editing a file, always jump to the last known cursor position.
  " Don't do it when the position is invalid or when inside an event handler
  autocmd BufReadPost *
    \ if line("'\"") > 0 && line("'\"") <= line("$") |
    \   exe "normal g`\"" |
    \ endif

  augroup END

else

  set autoindent		" always set autoindenting on

endif " has("autocmd")

" STEELJ
set tabstop=2
set shiftwidth=2
set expandtab
filetype on
:nnoremap <silent> <F8> :Tlist <CR>
set smartcase
set nu
set cursorline
:vnoremap * y/<C-R>"<CR>
:set foldmethod=manual
:map + v%zf
set laststatus=2
set nomousehide
set mouse=a
" unmap ctrl-W in insert mode
:map!  <Nop>
:map!  <Nop>
let g:load_doxygen_syntax=1
"let g:doxygen_enhanced_colour=1
"ctags switch files
":nnoremap <silent> <F11> :!switchtags.sh <CR>
":nnoremap <silent> <F12> :!mytags.sh <CR>
:nnoremap <silent> <F12> :!ctags -R --c++-kinds=+p --fields=+iaS --extra=+q<CR>
" syntax folding
set foldmethod=syntax
set foldlevelstart=99
" Project
"map <A-S-p> :Project<CR>
"map <A-S-o> :Project<CR>:redraw<CR>/
nmap <silent> <F3> <Plug>ToggleProject
let g:proj_window_width = 30
let g:proj_window_increment = 50
let g:proj_flags = "ibsSt"
:let Grep_Default_Filelist = '*.cpp *.h'
" Most Recently Used
map <F2> :MRU<CR>
let MRU_Max_Entries = 20
"DoxyTag
let g:DoxygenToolkit_endCommentTag="* \<enter>* History:\<enter>* - " . strftime("%Y/%m/%d") . ": STEELJ  - Initial Version\<enter>*/"
let g:DoxygenToolkit_authorName="STEELJ"
iab Hist - <C-R>=strftime("%Y/%m/%d")<CR>: STEELJ  -
iab /*** /******************************************************************************<CR>*<CR>*******************************************************************************/<up>
" background coloring in edit mode
:highlight LineNr ctermfg=red guifg=red
"au InsertEnter * :highlight LineNr ctermfg=15 ctermbg=1<cr>
au InsertEnter * :highlight LineNr cterm=reverse gui=reverse
au InsertLeave * :highlight LineNr cterm=NONE gui=NONE

" goto next error with F5
map <F5> :cnex<cr>

" toggle line wrap with F4
set nowrap
map <F4> :set nowrap! <cr>
let loaded_totd = 0

" Fix Term in Screen
if $TERM == 'screen'
  set term=xterm
endif

" colors
" blue on green
" hi DiffAdd        ctermfg=4 ctermbg=2
" grey bg
hi DiffAdd         ctermbg=7
" yellow on green
hi DiffChange     ctermfg=4 ctermbg=2
hi DiffDelete     ctermfg=4 ctermbg=6
" white on green
hi DiffText       ctermfg=7 ctermbg=2
