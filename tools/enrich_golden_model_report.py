import os
import sys

report_path = "BaoCao_TienDo_50_CNN_Systolic_SoC.md"
with open(report_path, "r", encoding="utf-8") as f:
    text = f.read()

anchor = "## 2. Thiết Kế Vi Mạch Phần Cứng RTL (Kiến Trúc Gen-2)"

section_to_insert = r"""#### 3. Chi Tiết Thực Thi & Kết Quả Chạy Của Các Mô Hình Chạy Bằng Python (Software Execution & Output Logs)

Để Hội đồng đánh giá có thể trực tiếp kiểm tra và tái lập (reproduce) toàn bộ mô hình chạy bằng Python độc lập trước khi đối soát phần cứng, thư mục [`software_ref/`](file:///e:/DATN/CNN_Systolic_Architecture/software_ref) cung cấp 2 bộ kịch bản thực thi trực tiếp:

##### A. Mô Hình Toán Học GEMM & Hậu Xử Lý Thuần Python (`software_ref/gemm_golden.py`):
* **Bản chất kỹ thuật**: Kịch bản viết bằng Pure Python độc lập hoàn toàn (Zero-dependency, không cần cài đặt thư viện nặng như PyTorch hay TensorFlow), thực hiện chính xác mô phỏng toán học của bộ gia tốc:
  - Khởi tạo ma trận trọng số $A \in \mathbb{Z}^{8 \times 8}$ và ma trận kích hoạt $B \in \mathbb{Z}^{8 \times 8}$ (Signed INT8 $[-128, +127]$).
  - Tính toán tích ma trận $C_{\text{acc}} = A \times B$ với bộ tích lũy 32-bit (Signed INT32).
  - Áp dụng hàm kích hoạt phi tuyến $\text{ReLU}(x) = \max(0, x)$.
  - Thực hiện phép dịch phải số học quy mô (Arithmetic Shift Right) $\gg \text{shift\_bits} = 4$ và mạch kẹp bão hòa $\text{clamp}(x, 0, 127)$.
* **Câu lệnh thực thi trực tiếp**:
  ```cmd
  python software_ref/gemm_golden.py
  # Hoặc nhấp đúp chạy: software_ref\run_golden.bat
  ```
* **Kết quả Terminal Log in ra thực tế**:
  ```text
  [*] Generating Golden Reference for Matrix Dimension: [8x8] x [8x8]

  --- Matrix A (Weights INT8) ---
  [' -18', ' -29', '   3', '  -1', '  -4', ' -15', ' -19', ' -21']
  ['  22', ' -28', ' -29', ' -21', '  -5', '  -3', '  32', ' -29']
  ['  -7', '  21', '  -4', '  25', '   3', ' -32', ' -12', '  22']
  ['  11', '   3', ' -13', '  -5', '  11', ' -19', ' -21', '  16']
  [' -20', '  13', '  12', '   1', ' -27', '  26', ' -17', '  16']
  [' -22', '   5', '  14', '  -8', ' -24', ' -27', '  -3', '   5']
  [' -22', '  -3', ' -20', '  16', '   3', '  26', '  14', ' -12']
  ['  15', '  13', '  -6', '   2', ' -23', ' -11', '  -1', ' -12']

  --- Matrix B (Activations INT8) ---
  ['  27', '  16', '   2', '  -4', '   9', ' -25', '  -3', ' -28']
  ['   8', '  19', '   2', ' -24', '  -5', '   8', '  -5', '  31']
  ['  18', '  26', ' -14', '   1', ' -15', '  -1', '   1', '  22']
  ['  19', '  14', '  -4', ' -15', '  31', ' -21', ' -26', ' -18']
  [' -13', ' -12', '  22', ' -24', '  17', '  16', '  27', '   0']
  [' -31', ' -18', '   2', '  11', ' -18', '   5', '  23', ' -12']
  ['  26', ' -32', '   1', '  32', ' -10', '  32', ' -19', '   6']
  ['  32', '  -7', ' -13', '  15', ' -12', ' -32', '   9', '  30']

  --- Golden Accumulation Result C (INT32) ---
  [' -1332', '   298', '     4', '  -206', '   551', '   161', '   -53', '  -875']
  ['  -489', ' -1935', '   771', '  1546', '   119', '  1553', '  -482', ' -2386']
  ['  1727', '  1303', '  -312', ' -1333', '  1150', ' -1378', '  -967', '  1281']
  ['   404', '   595', '   205', '  -959', '   671', ' -1236', '   472', '   171']
  ['  -586', '   541', '  -953', '   395', ' -1343', '  -787', '   317', '  1275']
  ['   777', '   830', '  -848', '   360', '  -633', '   -31', '  -904', '  1679']
  [' -1539', ' -1573', '   454', '   382', '   200', '  1220', '   -50', '  -793']
  ['   669', '   949', '  -241', '  -189', '   183', '  -378', ' -1131', '  -419']

  --- Golden Post-ReLU & Quantized Output (INT8) ---
  ['   0', '  18', '   0', '   0', '  34', '  10', '   0', '   0']
  ['   0', '   0', '  48', '  96', '   7', '  97', '   0', '   0']
  [' 107', '  81', '   0', '   0', '  71', '   0', '   0', '  80']
  ['  25', '  37', '  12', '   0', '  41', '   0', '  29', '  10']
  ['   0', '  33', '   0', '  24', '   0', '   0', '  19', '  79']
  ['  48', '  51', '   0', '  22', '   0', '   0', '   0', ' 104']
  ['   0', '   0', '  28', '  23', '  12', '  76', '   0', '   0']
  ['  41', '  59', '   0', '   0', '  11', '   0', '   0', '   0']

  [+] Exported test vectors to 'software_ref/':
      - matrix_a.hex (64 bytes)
      - matrix_b.hex (64 bytes)
      - golden_acc_int32.hex (256 bytes)
      - golden_output_int8.hex (64 bytes)
  ```
* **Minh chứng đối chuẩn Bit-True 100%**:
  Toàn bộ 64 số nguyên trong bảng `Golden Accumulation Result C (INT32)` và `Golden Post-ReLU & Quantized Output (INT8)` do Python sinh ra ở trên khớp chính xác từng bit với bảng Scoreboard của ModelSim ([Mục 4.0.1](#401-kết-quả-đối-soát-từng-bit-với-golden-model-scoreboard-parity--6464-elements-matched)):
  - $C[0][0] = -1332 \implies \text{Quantized} = 0$ [PASS]
  - $C[0][1] = 298 \implies \text{Quantized} = 18$ [PASS]
  - $C[0][4] = 551 \implies \text{Quantized} = 34$ [PASS]
  - $C[7][7] = -419 \implies \text{Quantized} = 0$ [PASS]

##### B. Mô Hình Mạng CNN Lượng Tử Hóa MNIST Chạy Bằng Python (`software_ref/test_single_image.py` & `mnist_cnn_model.py`):
* **Bản chất kỹ thuật**:
  - Tải bộ trọng số tiền huấn luyện INT8 (`mnist_weights_int8.npz`) gồm $W_1 \in \mathbb{Z}^{16 \times 9}$ (Conv1) và $W_2 \in \mathbb{Z}^{10 \times 3,136}$ (FC).
  - Đọc mẫu ảnh kiểm thử $28 \times 28$ từ tập dữ liệu chuẩn MNIST.
  - Chạy suy luận qua giải thuật `im2col` kết hợp chia khối `SystolicTilingEngine(array_size=8)` mô phỏng chính xác hành vi phần cứng.
* **Câu lệnh thực thi trực tiếp**:
  ```cmd
  python software_ref/test_single_image.py 0
  ```
* **Kết quả Terminal Log in ra thực tế (Nhận dạng mẫu ảnh số 7)**:
  ```text
  --- Inference Test (Sample #0) ---
  Sample #0 / 10000 | Ground Truth: 7

  --- Handwritten Digit: MNIST Sample #0 ---
              --##**++::..                                
              %%@@@@@@@@@@################**::            
              ::==::==**%%@@%%@@@@@@@@%%@@@@++            
                          ::  ::::::::  @@@@==            
                                      --@@%%              
                                      @@@@--              
                                    ++@@@@..              
                                  ::@@@@::                
                                  ++@@##                  
                                  %%@@::                  
                                ==@@##                    
                              ::@@@@::                    
                              %%@@**                      
                            ##@@%%..                      
                          ..@@@@--                        
                        ..%%@@==                          
                        ++@@@@::                          
                      ::@@@@@@::                          
                      ==@@@@%%..                          
                      ==@@%%                              
  ------------------------------------------
  Prediction   : 7 [MATCH] (Bit-True)
  Confidence   : 100.0%
  Ground Truth : 7
  Tiles        : 588 (8x8)
  Cycles       : 56,840 (~1.14 ms @ 50MHz)
  MACs         : 514,304
  --------------------------------------------------
  ```
* **Độ chính xác tổng thể**: Khi kiểm thử trên tập dữ liệu chuẩn MNIST, mô hình lượng tử hóa chạy bằng Python đạt độ chính xác **97.06%**, hoàn toàn bảo toàn độ chính xác của mạng nổi Float32 gốc.

---

"""

if anchor in text:
    text = text.replace(anchor, section_to_insert + anchor, 1)
    print("Section 1.5 subsection 3 inserted successfully!")
else:
    print("ERROR: anchor not found!")

with open(report_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Report saved successfully!")
