time ./oscheckperf all IO_TOOL=sysbench -f servers.txt \
  SYSBENCH_PROFILES="seqrd seqwr" \
  IO_TOTAL_SIZE=3G \
  SYSBENCH_FILE_NUM=4 \
  SYSBENCH_BLOCK_SIZE=16K \
  SYSBENCH_IO_MODE=sync \
  SYSBENCH_EXTRA_FLAGS=direct \
  SYSBENCH_THREADS=4 \
  SYSBENCH_DURATION=600 >> 1.log 2>&1


time ./oscheckperf all IO_TOOL=fio -f servers.txt \
  FIO_PROFILES="read write" \
  IO_TOTAL_SIZE=3G \
  FIO_FILE_NUM=4 \
  FIO_BS=16K \
  FIO_IOENGINE=sync \
  FIO_DIRECT=1 \
  FIO_NUMJOBS=4 \
  FIO_IODEPTH=1 \
  FIO_DURATION=600 >> 1.log 2>&1
