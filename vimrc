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

" --------------------
" TagList
" --------------------
" F4:  Switch on/off TagList
nnoremap <silent> <F4> :TlistToggle<CR>

" TagListTagName  - Used for tag names
highlight MyTagListTagName gui=bold guifg=Black guibg=Orange
" TagListTagScope - Used for tag scope
highlight MyTagListTagScope gui=NONE guifg=Blue
" TagListTitle    - Used for tag titles
highlight MyTagListTitle gui=bold guifg=DarkRed guibg=LightGray
" TagListComment  - Used for comments
highlight MyTagListComment guifg=DarkGreen
" TagListFileName - Used for filenames
highlight MyTagListFileName gui=bold guifg=Black guibg=LightBlue

"let Tlist_Ctags_Cmd = $VIM.'/vimfiles/ctags.exe' " location of ctags tool
let Tlist_Show_One_File = 1 " Displaying tags for only one file~
let Tlist_Exist_OnlyWindow = 1 " if you are the last, kill yourself
let Tlist_Use_Right_Window = 1 " split to the right side of the screen
let Tlist_Sort_Type = "name" " sort by order or name
let Tlist_Display_Prototype = 1 " do not show prototypes and not tags in the taglist window.
let Tlist_Compart_Format = 1 " Remove extra information and blank lines from the taglist window.
let Tlist_GainFocus_On_ToggleOpen = 1 " Jump to taglist window on open.
let Tlist_Display_Tag_Scope = 1 " Show tag scope next to the tag name.
let Tlist_Close_On_Select = 1 " Close the taglist window when a file or tag is selected.
let Tlist_Enable_Fold_Column = 0 " Don't Show the fold indicator column in the taglist window.
let Tlist_WinWidth = 40
let Tlist_Ctags_Cmd = 'ctags --c++-kinds=+p --fields=+iaS --extra=+q --languages=c++'
" very slow, so I disable this
let Tlist_Process_File_Always = 1 " To use the :TlistShowTag and the :TlistShowPrototype commands without the taglist window and the taglist menu, you should set this variable to 1.
":TlistShowPrototype [filename] [linenumber] 


" STEELJ
set tabstop=2
set shiftwidth=2
set expandtab
filetype on
:nnoremap <silent> <F8> :Tlist <CR>
set ignorecase
set nu
:vnoremap * y/<C-R>"<CR>
"set tags=~/Projects/Branch4.0/DCM_IO/Application/tags
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

let loaded_totd = 1


