# 規格填寫方式

建議同時保留三種格式：

- `interface_spec.yaml`：介面、型別、單位、範圍、錯誤碼、Init 與週期資訊；Python 可直接讀取。
- `test_vectors.csv`：每列一個正式測試案例，適合 Excel 編輯與版本比較。
- Markdown：補充狀態圖、公式、時序、需求理由與人工判讀內容。

至少要填：輸入、輸出、參數、合法範圍、錯誤碼、初始化值、Reset 行為、呼叫週期、容許誤差，以及 3–5 個已知正確答案。

測試類別建議包含：formal、normal、initialization/reset、boundary、equivalence partition、state transition、timing/sequence、error injection、fault recovery、out-of-range、numeric/overflow、random/fuzz、multi-instance、long-run、determinism、performance、static analysis 與 coverage。
