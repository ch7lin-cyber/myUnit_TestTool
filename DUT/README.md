# DUT 放置區

每一個被測 Function Block 使用獨立資料夾：

```text
DUT/
└─ FB_xxx/
   ├─ FB_xxx.c
   ├─ FB_xxx.h
   ├─ Dependency/
   │  ├─ project_types.h
   │  └─ utility.c
   └─ CMakeLists.txt
```

請一併放入自有的 header、macro、typedef、enum 與外部函式實作。不要放 MCU SDK 的整包原始碼；硬體相依函式請在 `Test/mocks/` 建立 mock。

測試完成後，`tools/write_test_comment.py` 會在指定的 `.c` 或 `.h` 開頭插入或更新一段有界標記註解，不會修改 Function Block 的演算法內容。
