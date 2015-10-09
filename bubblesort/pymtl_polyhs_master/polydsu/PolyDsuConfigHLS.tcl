#=========================================================================
# PolyDsuConfigHLS.tcl
#=========================================================================

set top "PolyDsuConfigHLS"

# In case this script is run from a different directory, we use the
# actual script name to figure out where the corresponding source code
# is located.

set sproj_dir [file dirname [info script]]
set src_dir "${sproj_dir}/.."
puts "Subproject directory path: ${sproj_dir}"

open_project $top.prj

set_top $top

add_files -cflags "-I$src_dir" $sproj_dir/$top.cc

open_solution "solution1" -reset

set_part {xc7z020clg484-1}
create_clock -period 10

config_rtl -reset state

set_directive_interface -mode ap_ctrl_none $top

set_directive_interface -mode ap_hs $top xcelreq
set_directive_interface -mode ap_hs $top xcelresp

set_directive_data_pack $top dsTable.table

csynth_design

# concatenate all the verilog files into a single file
set fout [open ./$top.v w]
fconfigure $fout -translation binary
set vfiles [glob -nocomplain -type f "$top.prj/solution1/syn/verilog/*.v"]
foreach vfile $vfiles {
  set fin [open $vfile r]
  fconfigure $fin -translation binary
  fcopy $fin $fout
  close $fin
}

# add verilator lint off and on pragmas
seek $fout 0
puts -nonewline $fout "/* verilator lint_off WIDTH */\n\n//"
seek $fout -1 end
puts $fout "\n\n/* lint_on */"

close $fout

exit
