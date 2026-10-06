# Bonus B1 - Prebuilt vs source build

Host `Windows-AMD64` · CPU `AMD Ryzen 5 5600H with Radeon Graphics`
Vector extensions recorded by hardware probe: not available
llama.cpp `b10488` both sides · `threads=6` ·
**both pinned to `ngl=0`** so this isolates the compiler ·
metric `tg128`, 3 repetitions

> **Backend mismatch, handled.** The prebuilt binary sees
> `['CUDA0: NVIDIA GeForce RTX 3050 Laptop GPU (4095 MiB, 3305 MiB free)']` and your source build sees `(no devices)`.
> Left at `-ngl 99` this comparison would have measured the accelerator and printed
> it under a compiler headline, so both sides were pinned to `-ngl 0`.

| Binary | Built for | tg128 (tok/s) | Relative |
|:--|--:|--:|--:|
| prebuilt release | runtime CPU dispatch | 18.1 | 1.00x |
| your source build | this CPU (`-DGGML_NATIVE=ON`) | 9.7 | 0.54x |

On this machine, the prebuilt binary is **1.86x faster**.

before: 18.1 tok/s (prebuilt release)
after:  9.7 tok/s (source build, -DGGML_NATIVE=ON)
speedup: 0.54x

Both binaries are tagged b10488 and run the same model on CPU. The release is a
prebuilt multi-variant Windows package; the source build uses MinGW GCC 14.2,
`-O3 -march=native` (`znver3`), and a single static CPU backend. Compiler,
runtime dispatch, and packaging therefore differ together. This test does not
isolate the effect of `-DGGML_NATIVE=ON` alone.



## Build and interpretation

The source tree was cloned at tag `b10488` and built in Release with Ninja,
MinGW GCC 14.2, `-DGGML_NATIVE=ON`, and `-DGGML_CUDA=OFF`. Windows compilation
also required `-D_WIN32_WINNT=0x0A00` for both C and C++ flags. The build log
contains `-O3 -march=native`; GCC resolves that to `znver3` on this Ryzen 5
5600H and reports AVX2/FMA enabled, AVX-512F disabled. The Windows hardware
probe did not record extensions, so the earlier "none" line was an absence of
probe data, not a CPU capability result.

The release folder contains separate `ggml-cpu-*.dll` variants, including a
Haswell AVX2 variant; it can dispatch to a suitable optimized kernel at
runtime. That is a concrete reason a generic downloadable package can beat
this particular native build. At Q4's ~2.97 GiB and only 9.7-18.1 decode
tokens/s on CPU, repeated weight reads plausibly make memory bandwidth a
major cost, but this experiment did not measure bandwidth or profile the
kernels. The 1.86x gap is therefore an observed *binary/toolchain* result,
not proof of a single compiler-flag or memory-bandwidth cause. The main lab
uses CUDA offload and is benchmarked separately.

To reproduce the source build on this Windows machine, add the virtual
environment's `Scripts` directory to `PATH` for Ninja, then run:

```powershell
cmake -S bonus/llama.cpp -B bonus/llama.cpp/build -G Ninja `
  -DCMAKE_C_COMPILER=C:/msys64/mingw64/bin/gcc.exe `
  -DCMAKE_CXX_COMPILER=C:/msys64/mingw64/bin/g++.exe `
  -DGGML_NATIVE=ON -DGGML_CUDA=OFF -DCMAKE_BUILD_TYPE=Release `
  -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=ON `
  '-DCMAKE_C_FLAGS=-D_WIN32_WINNT=0x0A00' `
  '-DCMAKE_CXX_FLAGS=-D_WIN32_WINNT=0x0A00'
cmake --build bonus/llama.cpp/build --target llama-bench -j 6
.\lab.ps1 compare-builds
```
