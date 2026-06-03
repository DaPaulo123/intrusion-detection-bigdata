# UNSW-NB15 Data Dictionary

Bộ dữ liệu **UNSW-NB15** là bộ dữ liệu thực tế được thiết kế chuyên biệt cho hệ thống Phát hiện Xâm nhập (IDS/IPS). Bộ trường dữ liệu bao gồm 49 đặc trưng (features) tổng cộng từ quá trình phân tích luồng gói tin mạng thực tế.

*(Lưu ý: Trên các tệp Training/Testing định dạng sẵn cho Machine Learning, một số trường thông tin định danh như IP, Cổng (Port), và Thời gian (Time) đôi khi bị lược bỏ hoặc thay thế bằng cột `id`, khiến số cột còn 45 cột. Dưới đây là danh sách toàn bộ 49 thuộc tính nguyên bản của tập dữ liệu này)*

## Nhóm Đặc Trưng Đầu Luồng (Flow Features) & Cơ Bản

| STT | Tên Cột | Ý Nghĩa (Định nghĩa) |
| --- | --- | --- |
| 1 | `srcip` | Địa chỉ IP nguồn (Source IP) |
| 2 | `sport` | Cổng nguồn (Source port) |
| 3 | `dstip` | Địa chỉ IP đích (Destination IP) |
| 4 | `dsport` | Cổng đích (Destination port) |
| 5 | `proto` | Giao thức truyền tải (ví dụ: tcp, udp, arp, ospf...) |
| 6 | `state` | Trạng thái kết nối (Connection state) ví dụ: FIN, CON, REQ, INT... |
| 7 | `dur` | Tổng thời gian của luồng mạng (Duration) |
| 8 | `sbytes` | Tổng số byte chuyển từ Source (nguồn) đến Destination (đích) |
| 9 | `dbytes` | Tổng số byte chuyển từ Destination đến Source |
| 10 | `sttl` | Time to live (TTL) cấu hình từ Source |
| 11 | `dttl` | Time to live (TTL) cấu hình từ Destination |
| 12 | `sloss` | Số tập tin của Source bị drop (rớt)/retransmitted (gửi lại) |
| 13 | `dloss` | Số tập tin của Destination bị drop (rớt)/retransmitted (gửi lại) |
| 14 | `service` | Dịch vụ phân loại (http, ftp, smtp, ssh, dns... '-' nếu không rõ) |
| 15 | `sload` | Băng thông chiều lên - từ Source (bits per second) |
| 16 | `dload` | Băng thông chiều xuống - tới Destination (bits per second) |
| 17 | `spkts` | Số gói tin truyền từ Source sang Destination |
| 18 | `dpkts` | Số gói tin truyền từ Destination sang Source |

## Nhóm Đặc Trưng Nội Dung (Content Features) & TCP

| STT | Tên Cột | Ý Nghĩa (Định nghĩa) |
| --- | --- | --- |
| 19 | `swin` | Giá trị TCP window advertisement quảng bá bởi Source |
| 20 | `dwin` | Giá trị TCP window advertisement quảng bá bởi Destination |
| 21 | `stcpb` | (TCP base sequence number) Số trình tự gốc của TCP cho Source |
| 22 | `dtcpb` | Số trình tự gốc của TCP cho Destination |
| 23 | `smean` | Kích thước trung bình (Mean) của gói tin xuất phát từ Source |
| 24 | `dmean` | Kích thước trung bình (Mean) của gói tin xuất phát từ Destination |
| 25 | `trans_depth` | Độ sâu đường dẫn (pipelined depth) vào kết nối của HTTP request/response |
| 26 | `response_body_len`| Kích thước nội dung (chưa nén) của dữ liệu HTTP server trả về |

## Nhóm Đặc Trưng Thời Gian (Time Features)

| STT | Tên Cột | Ý Nghĩa (Định nghĩa) |
| --- | --- | --- |
| 27 | `sjit` | Tham số Jitter đo được từ Source (mSec) |
| 28 | `djit` | Tham số Jitter đo được từ Destination (mSec) |
| 29 | `stime` | Thời gian bắt đầu bản ghi (Start time) |
| 30 | `ltime` | Thời gian kết thúc bản ghi (Last time) |
| 31 | `sintpkt` | Thời gian giãn cách giữa các gói tin ở Source (Interpacket arrival time) |
| 32 | `dintpkt` | Thời gian giãn cách giữa các gói tin ở Destination |
| 33 | `tcprtt` | Thời gian vòng TCP (Round-trip time setup) = `synack` + `ackdat` |
| 34 | `synack` | Thời gian thiết lập TCP (giữa gói SYN và SYN_ACK) |
| 35 | `ackdat` | Thời gian thiết lập TCP (giữa gói SYN_ACK và ACK) |

## Nhóm Đặc Trưng Khởi Tạo Tập Trung (General Purpose Features / Connection counts)

Các đặc trưng này thể hiện phân tích logic trên nhóm 100 luồng (connections) kết nối cuối cùng gần nhất với bản ghi đang xét.

| STT | Tên Cột | Ý Nghĩa (Định nghĩa) |
| --- | --- | --- |
| 36 | `is_sm_ips_ports` | Giá trị `1` nếu IP/Port Nguồn và IP/Port Đích giống nhau, ngược lại `0` |
| 37 | `ct_state_ttl` | Mã số cho mỗi trạng thái phụ thuộc vào dải giá trị TTL theo Source/Destination |
| 38 | `ct_flw_http_mthd`| Tổng số lượng luồng chứa các method (GET/POST) của dịch vụ HTTP |
| 39 | `is_ftp_login` | Giá trị `1` nếu tài khoản FTP được truy cập bằng user và password, ngược lại `0` |
| 40 | `ct_ftp_cmd` | Số luồng chứa một câu lệnh (command) trong phiên FTP |
| 41 | `ct_srv_src` | Số lượng kết nối cùng chung Service và Source IP |
| 42 | `ct_srv_dst` | Số lượng kết nối cùng chung Service và Destination IP |
| 43 | `ct_dst_ltm` | Số lượng kết nối chung Destination IP (có tính tới last time) |
| 44 | `ct_src_ltm` | Số lượng kết nối chung Source IP (có tính tới last time) |
| 45 | `ct_src_dport_ltm`| Số luồng kết nối chung Source IP và Destination Port |
| 46 | `ct_dst_sport_ltm`| Số luồng kết nối chung Destination IP và Source Port |
| 47 | `ct_dst_src_ltm` | Số lần Source IP được kết nối tới Destination IP |

## Nhóm Phân Loại Kẻ Tấn Công (Label Features)

| STT | Tên Cột | Ý Nghĩa (Định nghĩa) |
| --- | --- | --- |
| 48 | `attack_cat` | **Nhãn đa lớp:** Tên của phân loại tấn công: Analysis, Backdoors, DoS, Exploits, Fuzzers, Generic, Reconnaissance, Shellcode, Worms (để trống nếu lưu lượng bình thường) |
| 49 | `label` | **Nhãn nhị phân:** `0` đại diện cho lưu lượng bình thường (Normal), `1` đại diện cho hành vi tấn công (Attack record) |
