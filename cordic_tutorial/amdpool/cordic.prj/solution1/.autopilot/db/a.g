#!/bin/sh
lli=${LLVMINTERP-lli}
exec $lli \
    /home/student/mq58/MengProj/meng-reconfigurable-computing/cordic_tutorial/amdpool/cordic.prj/solution1/.autopilot/db/a.g.bc ${1+"$@"}