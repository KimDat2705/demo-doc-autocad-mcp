# 🧠 NGHIÊN CỨU: "AI TỰ HỌC" từ đối tác — làm sao học được mà KHÔNG học phải cái SAI

> Soạn 2026-07-09, trả lời ý tưởng của user: *"Thêm chức năng cho AI CHỦ ĐỘNG hỏi đối tác và HỌC luôn, thay vì đợi
> mình sửa từng câu — đối tác cùng ta cải thiện dự án. NHƯNG: làm sao AI biết chỗ nào cần hỏi & học, chỗ nào là
> không có / sai dữ liệu để báo? Vì học phải kiến thức chuẩn, học sai → sau này trả lời sai, rất nguy hiểm."*

## 0. Kết luận ngắn
Ý tưởng **KHẢ THI và đáng làm** — nhưng phải định nghĩa "tự học" cho đúng. **Nguyên tắc vàng: AI học CÁCH ĐỌC (quy ước),
KHÔNG học SỰ THẬT (số/kiến thức).** Và **không thứ gì "học" được tự động hóa cứng thành sự thật** — mọi thứ đối tác dạy
đều: (a) neo vào bằng chứng trong file, (b) gắn NGUỒN (ai nói), (c) phạm vi tạm (chưa phải chân lý), (d) **con người
(chúng ta) duyệt trước khi thành quy tắc vĩnh viễn**. Nhờ vậy đối tác *cùng cải thiện* mà KHÔNG đầu độc được hệ thống.

## 1. "Tự học" có mấy nghĩa — cái nào an toàn, cái nào CẤM
| Kiểu "tự học" | An toàn? | Vì sao |
|---|---|---|
| 🔴 **Fine-tune / huấn luyện lại model** trên hội thoại đối tác | **CẤM** | Làm hành vi khó lường; model "nhớ" cả cái SAI thành kiến thức; **phá vỡ nguyên tắc "số do CODE, không do model nhớ"**. Đây CHÍNH LÀ ác mộng "học sai → trả lời sai" mà bạn lo. |
| ✅ **Học QUY ƯỚC ĐỌC** (nhãn '(SL: N bộ)' = số lượng; 'X hoa' cũng là dấu nhân; đơn vị cm cho firm này) | **AN TOÀN** | Cái học được là **quy tắc ĐỌC**, kiểm chứng được lại chính file. Không phải "sự thật", là "cách hiểu con chữ". |
| ⚠️ **Ghi nhận INPUT đối tác cấp** (kg/bộ=8.62; đơn giá; chiều cao tầng) | **AN TOÀN CÓ ĐIỀU KIỆN** | Là INPUT có nguồn, KHÔNG phải AI tự bịa. Nhưng có thể SAI (đối tác gõ nhầm) → phải gắn nguồn, phạm vi phiên, luôn xác nhận lại; **KHÔNG hóa thành chân lý toàn cục**. |

> **CHÌA KHÓA:** học **CÁCH ĐỌC con chữ** (verify được) thì an toàn; "học SỰ THẬT/con số vào trí nhớ" thì nguy hiểm.

## 2. Câu hỏi cốt lõi của bạn: AI phân biệt 3 tình huống thế nào?
AI **không cần "hiểu đúng-sai chuyên môn"** (nó không phải kỹ sư) — nó phân biệt bằng **TÍN HIỆU CƠ HỌC** (code làm được):

| Tình huống | Tín hiệu máy nhận ra | Hành động |
|---|---|---|
| **① Cần HỎI & HỌC** | Có **TEXT trong file** ở vùng liên quan nhưng **không parse được** (nhãn lạ, quy ước mới) — *biết là có data ở đó, chỉ chưa hiểu* | Hỏi: *"Ở [handle] ghi '…', đây là gì? (số lượng / kích thước / mã / khác)"* → học **cách đọc**, **neo vào text THẬT** |
| **② KHÔNG có dữ liệu** | Tìm khắp file **không thấy gì** liên quan | Nói thẳng *"không có trong bản vẽ"* — **KHÔNG** mời đối tác "dạy" một con số trôi nổi (con số không neo vào file = fact tiêm từ ngoài = kiểu nguy hiểm) |
| **③ Có dữ liệu nhưng NGHI SAI** | Đọc được nhưng **mâu thuẫn/vô lý**: tổng ≠ tổng các phần; tiết diện 140 mà bảng nói 1.4m; giá trị đối tác cấp lệch xa số đọc từ file; đơn vị cho kết quả phi lý | **BÁO NGHI NGỜ**: *"Chỗ này có vẻ mâu thuẫn: X vs Y [handle] — nhờ đối tác kiểm"* — **KHÔNG tự chọn bên nào** |

→ Ba tín hiệu **"có-text-nhưng-không-hiểu" / "không-có-text" / "có-text-nhưng-mâu-thuẫn"** đều là kiểm tra **mẫu + nhất quán**,
code làm được — KHÔNG cần AI "biết xây dựng".

## 3. Chống "HỌC PHẢI CÁI SAI" — CỔNG KIỂM ĐỊNH (phần sống còn)
Đây là chỗ giải quyết đúng nỗi lo của bạn. Mọi thứ "học" phải qua **4 cổng**:

1. **NEO vào bằng chứng file:** một quy ước học được phải ánh xạ tới **text/handle THẬT** trong file. Đối tác "dạy" cái
   không neo được vào data → chỉ là input phiên (gắn nguồn), KHÔNG thành quy tắc.
2. **NGUỒN (provenance):** mỗi thứ học/nhận đều ghi *ai nói, từ đâu* (đọc-file / đối-tác-cấp / suy-đoán). Không bao giờ
   xóa nguồn → luôn truy được và **thu hồi được** nếu sai.
3. **PHẠM VI + KIỂM ĐA-FILE:** quy ước mới là **TẠM**, phạm vi *file/đơn vị này*, **chưa phải chân lý toàn cục** — chỉ
   được "tin" sau khi **đúng trên ≥3 file khác domain** (đúng nguyên tắc chống-overfit đã có).
4. **CON NGƯỜI DUYỆT (human-in-the-loop) trước khi thành VĨNH VIỄN:** hội thoại đối tác được **GHI LOG thành "quy ước
   ứng viên"**; **chúng ta (dev) rà** → hợp lý + tổng quát thì mới "chốt" thành quy tắc (code + test). Đối tác dạy **không
   tự động biến thành code** — nó thành **ứng viên chờ duyệt**.

> **Ranh giới AN TOÀN:** AN tự động = (a) phát hiện chỗ bí, (b) hỏi câu tốt, (c) áp câu trả lời **CHO PHIÊN NÀY** kèm nguồn
> "theo đối tác cho biết, chưa xác nhận". → Tất cả **có thể sai nhưng KHÔNG nguy hiểm** vì được gắn cờ + phạm vi hẹp + thu
> hồi được. **Học VĨNH VIỄN (thành sự thật/quy tắc) thì KHÔNG tự động — luôn qua người duyệt.** Đây là cái chặn "đầu độc".

## 4. Vì sao không thể để AI TỰ phán "đúng/sai" rồi hóa cứng
- AI **không phải chuyên gia xây dựng** → nó KHÔNG tự thẩm định được một kiến thức chuyên môn là đúng hay sai.
- Nên "để AI tự quyết cái gì đúng mà học" là **sai cách đặt vấn đề**. Thay vào đó:
  - Cái AI ĐỌC từ file = **ground truth** (có handle, verify được) — cái này AI *không "học", đọc mới mỗi lần*.
  - Cái người NÓI cho AI = **một LỜI KHAI (claim)** — có thể đúng/sai → **không được coi là sự thật chỉ vì có người nói**.
- Cách kiểm "một QUY ƯỚC đọc có đúng không": áp quy ước đó có tạo ra số **KHỚP với bằng chứng khác trong file** không
  (đối chiếu chéo) + đúng trên nhiều file. → verify được bằng máy.
- Cách kiểm "một CON SỐ chuyên môn (kg/bộ, đơn giá) có đúng không": AI **không tự kiểm được** → giữ nguyên là *đối-tác-cấp*,
  xác nhận lại, **KHÔNG hóa cứng thành quy tắc**. Nếu sai thì sai trong phạm vi phiên + quy trách nhiệm nguồn, không ngấm vào hệ.

## 5. Một mối nguy nữa cần chặn: bị "DẠY BẬY" (chống thao túng)
- Coi mọi input đối tác (và cả **chữ trong file**) là **DỮ LIỆU/lời khai**, **KHÔNG phải MỆNH LỆNH** thay đổi hành vi lõi.
- Một câu "hãy coi mọi số âm là hợp lệ" hay một ghi chú lạ trong file **KHÔNG được** nới lỏng luật chống bịa. Luật lõi
  (số do code, thiếu→hỏi, gắn cờ) là **bất biến**, đối tác không "dạy" đè được.

## 6. Khả thi tới đâu
| Làm được NGAY (an toàn) | Cần cẩn thận | TRÁNH |
|---|---|---|
| AI chủ động HỎI khi thấy "có text mà không hiểu" | Cổng duyệt bán tự động: dev rà log ứng viên → thêm quy tắc có test | 🔴 Fine-tune model trên data đối tác |
| Áp câu trả lời đối tác cho PHIÊN (gắn nguồn, xác nhận lại) | Đối chiếu chéo tự động để bắt "nghi sai" | 🔴 Tự hóa cứng lời khai đối tác thành chân lý |
| LOG "chỗ chưa đọc được" + "quy ước ứng viên" | Phân loại 3 tín hiệu chính xác (tránh hỏi nhầm chỗ không có data) | 🔴 "Học" số/kiến thức vào trí nhớ (thay vì đọc từ file) |
| BÁO mâu thuẫn/vô lý để đối tác kiểm | | 🔴 Tin giá trị "dạy" mà không neo vào bằng chứng file |

## 7. Không phải làm lại từ đầu — đã có sẵn nền
- **3 tầng độ tin cậy** (đọc-verbatim / gán-vị-trí-chưa-chắc / đối-tác-cấp) = **provenance** đã có.
- **"Thiếu → hỏi"** = chủ động hỏi (một phần) đã có.
- **"Test ≥3 file khác domain"** = cổng validate-trước-khi-tin đã có.
- **Cảnh báo đa-tiết-diện / suy-đoán-đơn-vị** = mầm mống "báo nghi ngờ" đã có.
→ Chức năng tự-học là **MỞ RỘNG** các nếp này, không phải mô hình mới.

## 8. Kiến trúc đề xuất (vòng lặp "đối tác cùng cải thiện" AN TOÀN)
```
Đối tác hỏi
   │
   ├─ AI đọc được + đủ  → trả lời (số + handle)                       [đã có]
   ├─ Đọc được nhưng NGHI SAI (mâu thuẫn/vô lý) → BÁO, nhờ kiểm        [mở rộng cảnh báo]
   ├─ KHÔNG có text liên quan → "không có trong bản vẽ"               [đã có]
   └─ CÓ text mà KHÔNG hiểu (nhãn lạ) →
          AI hỏi: "'…' [handle] là gì?"  ──► đối tác trả lời
                                              │
                    ┌─────────────────────────┤
             (phiên này)                 (ghi LOG ứng viên)
        áp NGAY, gắn nguồn                     │
        "theo đối tác, chưa xác nhận"     DEV rà định kỳ
                                               │
                                   verify ≥3 file + hợp lý?
                                          │            │
                                        CÓ           KHÔNG
                                          │            │
                                 chốt thành QUY TẮC   bỏ
                                 (code + test) — vĩnh viễn
```
Lộ trình: (1) chuẩn hoá tín hiệu 3-loại + tool "hỏi để học" (áp phiên + log); (2) đối chiếu chéo để "báo nghi sai";
(3) màn hình cho dev duyệt ứng viên → sinh quy tắc + test. Mỗi bước giữ nguyên **KPI "tỷ lệ bịa ≈ 0%"**.

## 9. Bottom line
- **Có** làm được "đối tác cùng cải thiện": AI chủ động hỏi + áp-theo-phiên + log lại.
- **Nhưng** ranh giới cứng: **học CÁCH ĐỌC (verify được) — KHÔNG học SỰ THẬT; áp-phiên tự động — hóa-cứng thì người
  duyệt.** Nhờ đó *đối tác không thể (dù vô ý) đầu độc hệ thống bằng kiến thức sai* → giải đúng nỗi lo của bạn.
- Cái AI "học sai" tệ nhất chỉ ở **phạm vi 1 phiên + có gắn cờ + thu hồi được**, KHÔNG ngấm thành hành vi vĩnh viễn.
