# Jialing Workflow V2

影像先鎖、對白後製、逐鏡驗收的 AI 影片製作流程，包含 ComfyUI 無音軌 B-roll 範例、21 鏡分鏡規劃與技術 QC 工具。

**狀態：設計與匯入範例；尚未完成此 V2 套件的 Mac / ComfyUI 實機生成驗證。** JSON 結構檢查不代表節點相容性或生成效果已通過測試。

## 檔案

| 檔案 | 用途 |
| --- | --- |
| [Jialing_H3_MLX_Visual_Only.json](Jialing_H3_MLX_Visual_Only.json) | ComfyUI T2V 空景預覽，音訊輸出未連接 |
| [Jialing_21_Shot_Plan.csv](Jialing_21_Shot_Plan.csv) | 21 鏡規劃、角色連續性、參考圖需求與音訊後製 |
| [Jialing_Production_Pipeline_V2.md](Jialing_Production_Pipeline_V2.md) | 完整製作流程、替代引擎與人工驗收規則 |
| [Jialing_picture_qc.py](Jialing_picture_qc.py) | 解析度、FPS、時長、音軌與解碼檢查 |

## 使用方式

1. 準備 ComfyUI 與 [ComfyUI-MiniMax-H3-MLX-SolAttn](https://github.com/yshenaw/ComfyUI-MiniMax-H3-MLX-SolAttn) 節點，依上游說明安裝模型。此專案不附模型權重。
2. 將 JSON 拖入 ComfyUI；確認 `MiniMaxH3MLXTurbo`、`CreateVideo`、`SaveVideo` 節點可用。節點版本可能影響 widget 對應，排程前請逐項確認。
3. 範例預設為 `dense` attention、864×480、5 秒、24fps。先生成一鏡無人街景，再檢查成品。
4. 安裝 Python 3、FFmpeg 與 ffprobe，執行技術 QC：

```bash
python3 Jialing_picture_qc.py path/to/preview.mp4
python3 Jialing_picture_qc.py path/to/preview.mp4 --fps 24/1 --width 864 --height 480 --max-duration 15
```

回傳碼 `0` 表示所有輸入通過技術檢查，`1` 表示至少一項失敗。QC 會完整解碼影片，但不檢查人臉身份、角色人數、運鏡、年代或劇情連續性，這些仍需人工驗收。

若輸出意外含音軌，可另存無音軌版本，再跑 QC：

```bash
ffmpeg -i preview.mp4 -map 0:v:0 -an -c:v copy preview_picture_only.mp4
```

此 T2V 範例用於空景。人物主戲需另行準備角色圖紙與經驗證的 I2V / R2V 工作流程；角色圖、場景圖、配音與影片成品未包含於本套件。替代引擎與指令保留於流程文件作為待驗證方案，使用前請核對上游版本與硬體需求。

## 授權與來源

本儲存庫原創程式、工作流程與文件採 [MIT License](LICENSE)。第三方模型、節點、商標、既有影視角色／劇情及其他第三方素材的權利不由本授權授予；請依各自的授權使用。此專案與相關影視作品或模型供應商無官方隸屬關係。

上游參考：

- [ComfyUI MiniMax H3 MLX](https://github.com/yshenaw/ComfyUI-MiniMax-H3-MLX-SolAttn)
- [ComfyUI H3 文件](https://github.com/Comfy-Org/docs/blob/main/tutorials/video/minimax/minimax-h3-native.mdx)
- [LTX-2 MLX](https://github.com/dgrauet/ltx-2-mlx)
