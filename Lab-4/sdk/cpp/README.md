### 运行方法
1. 首次运行，需要配置CMake（在不改变CMakeLists.txt的情况下，不用重新运行这步）
```shell
mkdir build && cd build
cmake ..
```
2. 在build目录下，进行编译：（如果你刚执行了第一步，此时你便已经在build目录下了）
```shell
make
```
> 小提示：进入某个指定目录的方法是`cd <目录>`
3. 编译好后，就可以看到名为sdk的主程序了，直接执行它即可（注意`./`表示当前目录，不可省略）。
```shell
./sdk
```