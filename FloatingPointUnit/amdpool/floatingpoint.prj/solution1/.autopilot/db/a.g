#!/bin/sh
lli=${LLVMINTERP-lli}
exec $lli \
    /home/student/xt85/MENG/meng-reconfigurable-computing/FloatingPointUnit/amdpool/floatingpoint.prj/solution1/.autopilot/db/a.g.bc ${1+"$@"}
