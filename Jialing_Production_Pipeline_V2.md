# 《陳嘉玲》重製流程 V2 — 影像先鎖、對白後製、逐鏡驗收

**狀態：設計和匯入範例已完成；尚未在使用者的 Mac 或 ComfyUI 上實機執行。**

## A. 對現在這套 H3 MLX 節點的診斷
- `MiniMaxH3MLXTurbo` 原始碼必要輸入為 `prompt, model_profile, generation_profile, memory_mode, qwen_precision, attention, width, height, duration_seconds, seed`，附加設定有 `sol_tau, full20_fbc, stream_io`，**沒有影像參考輸入口**；內部使用 `StrictStagedTextToVideo`。因此再長的角色描述也不會讓它變成 I2V/R2V。
- 上游範例將生成的 AUDIO 直接接進 `CreateVideo` 並存出 WAV；「no music」文字不等於硬性禁止配樂。`Jialing_H3_MLX_Visual_Only.json` 已實際移除輸出端音訊連線，保留影片（但模型內部仍會算音訊）。
- 新範例使用 `dense`，避開目前部分 Mac 安裝的 `sol_attn` 原始碼編譯缺標頭問題。等到相同鏡頭、相同 seed 成功 A/B 且無破圖，才評估重新打開。

## B. 三條可執行的生成路徑
**B-roll 和非角色特寫：** 現有 ComfyUI H3 MLX T2V，用 `Jialing_H3_MLX_Visual_Only.json`。目標只做空巷、河堤、街景等；**不是人物主戲解法**。

**Mac 本地人物鏡頭（待測試）：** LTX-2.3 MLX I2V 路線，接受單張 `--image` 首幀；公開專案 `dgrauet/ltx-2-mlx` 在 Apple Silicon 有 I2V 範例，32GB 是建議門檻，先從 q4 小解析短片試，不保證單一圖片能完美維持不同鏡頭的身份。

示例（安裝 `ltx-2-mlx` 後，在自己的 Mac 上執行；未實機驗證）：
```bash
ltx-2-mlx generate --prompt 'Taiwan 1985. One 42-year-old Taiwanese mother, filmed in a locked medium close-up. The woman is completely still for a brief pause, then lowers her eyes. Natural late-afternoon light, restrained performance, no additional people, no camera movement.' --image mother_shot02_first_frame.png --distilled --model dgrauet/ltx-2.3-mlx-q4 -f 97 --frame-rate 24 -o shot02_draft.mp4
```
依本地輸出自行移除音軌：`ffmpeg -i shot02_draft.mp4 -map 0:v:0 -an -c:v copy shot02_picture_only.mp4`

**更強角色參考（需要別的執行環境／可能雲端）：** 官方 ComfyUI H3 `MiniMaxH3ReferenceToVideo` + `ref2va` checkpoint，可接角色、風格、動作、影片、音訊參考；或 `MiniMaxH3ImageToVideo` + `fl2va` 提供首尾幀。**它們不是目前 MLX T2V 的相同節點，也不能把 `LoadImage` 直接接到後者。** Mac 32GB 的 native PyTorch H3 影片生成未經本方案實測，不承諾可負擔。

## C. 在任何動態生成之前必須做好「電影角色圖紙」
一名演員一份 reference sheet（保留檔案版本與 prompt hash）：
1. 正面、中性表情；2. 左右 45°；3. 左右側面；4. 全身站姿；5. 表演表情（怒、忍住眼淚、失神）
- 嘉玲：單一臉型、單一制服、裙長、肩背、頭髮分線、髮長和膚色一致。
- 母親：單一臉型、短捲髮形狀、藍花布衣細節、深色長褲；停車時母親永遠站在巷道左側。
- 阿伯：只出現於隧道段落；服裝與老機車都要角色圖紙。
- 場景 bible：巷道主視角及反向視角、人物站位俯視平面、河堤、隧道，以及自行車、機車定裝照片。
- 對白段落至少一張指定構圖與光向的首幀；若支援，補尾幀或第二張表演參考。

## D. 片場級運鏡規則
- 先畫母女的 180° 攝影軸線：母在畫面左、嘉玲在右。正反打都保持彼此的視線方向；除非展示重新建立的全景，不任意跨軸。
- 主戲鏡頭 01–12 與 14：腳架固定。母親重大台詞只用穩定特寫，只有可辯護的敘事理由才推鏡；不用無意義的 orbit、pan、tilt、dolly。
- 嘉玲跑離：先固定方向讓人離畫，再切向同方向的鏡頭；不能憑空出現在上一場景。
- 搜尋戲：有兩個清楚的河堤空景；母親自行車上 **只有母親**，不可任何人載上車。
- 隧道：先建立嘉玲獨坐，再由阿伯進入，母親在這段 **完全不可見**。結尾在女孩表情停頓，不讓阿伯變成母親。

## E. 音訊工作流（永不把原生 H3 聲音當成定稿）
- Video track：只要無音訊影片。如果原生成輸出仍含音軌，FFmpeg `-an` 立即捨棄。
- Dialogue / ADR：先由通曉台語的演員校對台詞，選定台語腔調；錄製 48kHz / 24-bit mono 的乾聲，分角色、逐句存 WAV。禁止採用未驗證的自動台語唸稿作最終聲音。
- Foley：腳踏車鏈條、步伐、衣服、摩托車發動／行駛／煞停、兩聲喇叭；指定物件與遠近，不以單一模型聲音包混成。
- Ambience：小鎮、河堤、隧道分別錄/製作 30–60 秒 stereo room tone；用 crossfade 抑制跳切；河堤空曠，隧道需短反射聲。
- Music：預設 0，僅經人工決定是否另加配樂。資料夾、編輯時間線都要分離。
- Lip sync：先錄對白、再依長度挑有嘴形可控的鏡頭；沒有穩定對嘴技術時改用反應鏡、過肩鏡或畫外音，不冒險做近距離失真口型。

## F. 驗收與出片禁令
每個鏡頭驗收：角色數量（母女戲 2 人、阿伯不得出現）、臉和服裝、道具、站位、camera 是否符合分鏡、年代、音軌必須不存在、首尾連續性。人工核可才能入 Premiere。

**自動驗收只做可量測的項目**：FPS、解析度、音軌有無、長度、是否可解碼；臉部是否為同一人和腳踏車人數仍須逐鏡人工審查（或另接經驗證的視覺辨識模組，不能把工具輸出當絕對）。

最終輸出：24fps 主時間線，聲畫分軌，在 Premiere 完成 ADR、環境音、擬音、色彩和最終 QC；整片看過後才交片。

## 原始來源（供核對）
- https://github.com/yshenaw/ComfyUI-MiniMax-H3-MLX-SolAttn
- https://github.com/Comfy-Org/docs/blob/main/tutorials/video/minimax/minimax-h3-native.mdx
- https://github.com/dgrauet/ltx-2-mlx
