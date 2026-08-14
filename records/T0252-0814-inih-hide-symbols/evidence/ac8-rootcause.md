## 根因分析: 为何仅 -fvisibility=hidden 无效

inih 源 ini.h (L28-46) 定义 API 可见性宏:
  #ifdef _WIN32
    #define INI_API __declspec(dllexport/import)
  #elif __GNUC__ && !__MINGW32__
    #define INI_API __attribute__((visibility("default")))
  #else
    #define INI_API
  #endif

gcc 下 INI_API 显式声明 visibility("default")，会**覆盖**编译器的 -fvisibility=hidden。
因为 -fvisibility=hidden 只影响"未显式声明可见性"的符号。

修复: 传递 -DINI_API= 将宏覆盖为空串，声明变为普通函数，落回 hidden 默认。

验证: A/B 两个包目录的 libinih.a 提取 ini.c.o 用 readelf 对比
  6f0a3f82 (仅 fvisibility):  GLOBAL DEFAULT  ← 泄漏
  6d047740 (+DINI_API=):      GLOBAL HIDDEN   ← 正确
