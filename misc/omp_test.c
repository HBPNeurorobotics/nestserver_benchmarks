#define _GNU_SOURCE

#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sched.h>
#include <string.h>
 
int main(int argc, char* argv[])
{
  int pid = getpid();
  
  char hostname[128];
  memset(hostname, 0, 128);
  gethostname(hostname, 150);
  
  omp_set_num_threads(36);
  
#pragma omp parallel
  {
    int thread = omp_get_thread_num();
    int cpu = sched_getcpu();
    const char* msg = "process=%09d hostname=%s thread=%02d cpu=%02d\n";
    printf(msg, pid, hostname, thread, cpu);
  }
  
  return 0;
}
