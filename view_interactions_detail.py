#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看详细行为 / 代码操作 / AI 交互记录的辅助脚本

用法（在项目根目录）：
    python view_interactions_detail.py          # 默认查看最近 1 天的数据
    python view_interactions_detail.py 3        # 查看最近 3 天的数据
"""

import sys
import io
import os
import sqlite3
from datetime import datetime, timedelta

# Windows 控制台编码修复
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass


def get_db_path(cli_path: str = None) -> str:
    """
    获取 SQLite 数据库路径

    优先级：
    1. 命令行参数显式指定的路径
    2. 项目根目录下的 data/learning_analytics.db
    3. backend/data/learning_analytics.db（云端部署使用）
    """
    if cli_path:
        return os.path.abspath(cli_path)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "data", "learning_analytics.db"),
        os.path.join(base_dir, "backend", "data", "learning_analytics.db"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # 默认返回第一个路径，以便给出清晰的错误提示
    return candidates[0]


def main():
    # 解析天数参数，默认查看最近 1 天
    days = 1
    cli_db_path = None
    if len(sys.argv) >= 2:
        try:
            days = max(1, int(sys.argv[1]))
        except Exception:
            print("⚠️ 无法解析天数参数，使用默认 1 天。")
    if len(sys.argv) >= 3:
        cli_db_path = sys.argv[2]

    db_path = get_db_path(cli_path=cli_db_path)
    if not os.path.exists(db_path):
        print(f"❌ 找不到数据库文件：{db_path}")
        print("请先运行桌面应用，完成一次学习后再执行本脚本。")
        return

    # 统计起始时间（包含“今天”）
    days = max(1, days)
    start_dt = datetime.now() - timedelta(days=days-1)
    start_iso = start_dt.strftime('%Y-%m-%d %H:%M:%S')

    print(f"📂 使用数据库文件: {db_path}")
    print(f"⏱ 统计范围：最近 {days} 天 (从 {start_iso} 起)")
    print("=" * 80)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. 最近行为明细
    print("\n📝 最近的学习行为（最多显示 50 条）")
    print("-" * 80)
    try:
        cur.execute(
            """
            SELECT 
                b.timestamp,
                b.user_id,
                b.behavior_code,
                b.activity_name,
                s.platform AS device_label,
                json_extract(b.additional_data, '$.line_number')      AS line_number,
                json_extract(b.additional_data, '$.start_line')       AS start_line,
                json_extract(b.additional_data, '$.end_line')         AS end_line,
                json_extract(b.additional_data, '$.code_range')       AS code_range,
                json_extract(b.additional_data, '$.content_length')   AS content_len,
                json_extract(b.additional_data, '$.question_preview') AS q_preview,
                json_extract(b.additional_data, '$.response_preview') AS r_preview
            FROM learning_behaviors b
            LEFT JOIN user_sessions s ON b.session_id = s.session_id
            WHERE b.timestamp >= ?
            ORDER BY b.timestamp DESC
            LIMIT 50
            """,
            (start_iso,),
        )
        rows = cur.fetchall()
        if not rows:
            print("  (最近没有学习行为记录)")
        else:
            for r in rows:
                ts = r["timestamp"]
                uid = r["user_id"] or "unknown"
                device = r["device_label"] or "unknown-device"
                code = r["behavior_code"]
                name = r["activity_name"] or ""
                line = r["line_number"] or ""
                start_line = r["start_line"] or ""
                end_line = r["end_line"] or ""
                code_range = r["code_range"] or ""
                content_len = r["content_len"] or ""
                q_preview = r["q_preview"]
                r_preview = r["r_preview"]

                print(f"[{ts}] 用户:{uid} 设备:{device} 行为:{code}({name})", end="")
                extra = []
                if line:
                    extra.append(f"行={line}")
                if start_line or end_line:
                    extra.append(f"范围={start_line}-{end_line}")
                if code_range:
                    extra.append(f"区间={code_range}")
                if content_len:
                    extra.append(f"内容长度={content_len}")
                if extra:
                    print(" | " + "; ".join(str(x) for x in extra))
                else:
                    print()
                if q_preview:
                    print(f"    问题预览: {q_preview}")
                if r_preview:
                    print(f"    AI回复预览: {r_preview}")
    except Exception as e:
        print(f"  ⚠️ 查询学习行为出错: {e}")

    # 2. 最近代码操作明细
    print("\n💻 最近的代码操作（最多显示 50 条）")
    print("-" * 80)
    try:
        cur.execute(
            """
            SELECT 
                c.timestamp,
                c.user_id,
                c.operation_type,
                c.code_length,
                c.line_count,
                c.success,
                c.error_message,
                c.execution_time,
                json_extract(c.additional_data, '$.start_line') AS start_line,
                json_extract(c.additional_data, '$.end_line')   AS end_line,
                json_extract(c.additional_data, '$.code_range') AS code_range,
                s.platform AS device_label
            FROM code_operations c
            LEFT JOIN user_sessions s ON c.session_id = s.session_id
            WHERE c.timestamp >= ?
            ORDER BY c.timestamp DESC
            LIMIT 50
            """,
            (start_iso,),
        )
        rows = cur.fetchall()
        if not rows:
            print("  (最近没有代码操作记录)")
        else:
            for r in rows:
                ts = r["timestamp"]
                uid = r["user_id"] or "unknown"
                device = r["device_label"] or "unknown-device"
                op = r["operation_type"]
                ok = "成功" if r["success"] else "失败"
                print(f"[{ts}] 用户:{uid} 设备:{device} 操作:{op} - {ok}", end="")
                extra = []
                if r["code_length"] is not None:
                    extra.append(f"代码长度={r['code_length']}")
                if r["line_count"] is not None:
                    extra.append(f"行数={r['line_count']}")
                if r["start_line"] or r["end_line"]:
                    extra.append(f"范围={r['start_line']}-{r['end_line']}")
                if r["code_range"]:
                    extra.append(f"区间={r['code_range']}")
                if r["execution_time"] is not None:
                    try:
                        extra.append(f"耗时={float(r['execution_time']):.2f}s")
                    except Exception:
                        pass
                if extra:
                    print(" | " + "; ".join(str(x) for x in extra))
                else:
                    print()
                if r["error_message"]:
                    print(f"    错误信息: {r['error_message']}")
    except Exception as e:
        print(f"  ⚠️ 查询代码操作出错: {e}")

    # 3. 最近 AI 交互明细
    print("\n🤖 最近的 AI 交互（最多显示 50 条）")
    print("-" * 80)
    try:
        cur.execute(
            """
            SELECT 
                a.timestamp,
                a.user_id,
                a.interaction_type,
                a.question_length,
                a.response_length,
                a.response_time,
                json_extract(a.additional_data, '$.question_preview') AS q_preview,
                json_extract(a.additional_data, '$.response_preview') AS r_preview,
                s.platform AS device_label
            FROM ai_interactions a
            LEFT JOIN user_sessions s ON a.session_id = s.session_id
            WHERE a.timestamp >= ?
            ORDER BY a.timestamp DESC
            LIMIT 50
            """,
            (start_iso,),
        )
        rows = cur.fetchall()
        if not rows:
            print("  (最近没有 AI 交互记录)")
        else:
            for r in rows:
                ts = r["timestamp"]
                uid = r["user_id"] or "unknown"
                device = r["device_label"] or "unknown-device"
                it = r["interaction_type"]
                qlen = r["question_length"]
                rlen = r["response_length"]
                rt = r["response_time"]
                q_preview = r["q_preview"]
                r_preview = r["r_preview"]

                # 有些旧记录可能没有 response_time
                if rt is None:
                    rt_str = "未知"
                else:
                    try:
                        rt_str = f"{float(rt):.2f}s"
                    except Exception:
                        rt_str = str(rt)

                print(f"[{ts}] 用户:{uid} 设备:{device} 类型:{it} | 问长={qlen}字, 回答长={rlen}字, 响应时间={rt_str}")
                if q_preview:
                    print(f"    问: {q_preview}")
                if r_preview:
                    print(f"    答: {r_preview}")
    except Exception as e:
        print(f"  ⚠️ 查询 AI 交互出错: {e}")

    conn.close()
    print("\n✅ 明细查看完成。")
    print("提示：可以在命令后面加数字查看更长时间，例如：")
    print("  python view_interactions_detail.py 7   # 最近 7 天")


if __name__ == "__main__":
    main()


