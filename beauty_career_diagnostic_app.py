import streamlit as st
import pandas as pd
import json
import datetime

# ==========================================
# アプリケーション基本設定
# ==========================================
st.set_page_config(
    page_title="美容分野 キャリア・適性診断AIアプリ",
    page_icon="💄",
    layout="wide"
)

st.title("💄 美容分野 キャリア・適性診断AIアプリ")
st.caption("滋慶学園グループ「③ひとり一人を見てゆく視点」に基づく個別適性・キャリアビジョン発掘プラットフォーム")

# サイドバー設定
st.sidebar.header("👤 学生情報 & 入力モード")
student_name = st.sidebar.text_input("学生名 / ID", value="美容科1年 滋慶 華子")
course_type = st.sidebar.selectbox("所属コース", ["ヘアメイク・美容師コース", "メイク・ネイルコース", "エステ・コスメコース", "通信制課程", "リカレント・社会人コース"])
api_key = st.sidebar.text_input("API Key (任意: OpenAI/Gemini)", type="password", help="未入力時は内蔵のルールベース診断エンジンで動作します。")

# タブ構成
tab1, tab2, tab3 = st.tabs([
    "📝 1. 適性診断テスト（MBTI・嗜好・社会性）",
    "🎯 2. 診断結果＆おすすめ職種 TOP 3",
    "👩‍🏫 3. 教員用 1on1 面談ガイド & 成長ロードマップ"
])

# ------------------------------------------
# データ定義：美容分野の職種と特性
# ------------------------------------------
CAREER_DATABASE = {
    "美容師（ヘアスタイリスト / カラーリスト）": {
        "mbti_fit": ["ESFP", "ESTP", "ENFP", "ISFP"],
        "traits": ["1対1の密なコミュニケーション", "手先の器用さ", "トレンド感性", "体力・フットワーク"],
        "desc": "髪型やカラーを通して顧客の魅力を最大限に引き出し、自信を提供する美のスペシャリスト。",
        "strengths_match": "人と話すのが好きで、五感（手触り・立体感）を駆使した造形が得意な人に最適です。",
        "growth_path": "サロン実習で基礎技術を磨き、1 on 1の手元指導でカットラインの再現性を高めます。"
    },
    "ヘアメイクアーティスト / ブライダルスタイリスト": {
        "mbti_fit": ["ENFP", "INFJ", "ENTP", "ENFJ"],
        "traits": ["世界観の構築", "臨機応変な対応力", "共感力・ホスピタリティ", "チーム協働"],
        "desc": "撮影、舞台、結婚式など「特別な瞬間」の感動を演出し、トータルビューティを表現する仕事。",
        "strengths_match": "ストーリーや世界観を考えるのが好きで、人のハレの日に寄り添う情熱がある人に向いています。",
        "growth_path": "AIデザインシミュレーションで提案の幅を広げ、現場実習でホスピタリティを体得します。"
    },
    "ビューティアドバイザー（BA）/ コスメコンシェルジュ": {
        "mbti_fit": ["ESFJ", "ENFJ", "ISFJ", "ESTJ"],
        "traits": ["高い接客マナー", "傾聴・カウンセリング力", "成分・理論の探求", "笑顔のコミュニケーション"],
        "desc": "化粧品ブランドの顔として、お客様の肌の悩みに寄り添い最適なスキンケア・メイクを提案する仕事。",
        "strengths_match": "人の悩みを聞くのが好きで、理論立てて美しさの理由を説明することが得意な人にマッチします。",
        "growth_path": "「今日も笑顔であいさつを」の実践と、スキンケア成分・皮膚科学の確実な実学理解を深めます。"
    },
    "エステティシャン / セラピスト": {
        "mbti_fit": ["ISFJ", "INFJ", "ISFP", "ENFJ"],
        "traits": ["深い安心感の提供", "手のぬくもり・感覚（五感）", "リラクゼーション創出", "秘密保持・信頼性"],
        "desc": "オールハンドや最新機器の手技を通じ、顧客の心身の癒やしと肌の根本改善をもたらすスペシャリスト。",
        "strengths_match": "静かな環境で1対1で深く人と向き合うのが好きで、人の心身を癒やすことにやりがいを感じる人に適しています。",
        "growth_path": "手触りや圧力の加減など「五感、創造。」の感覚を研ぎ澄まし、カウンセリング技術を磨きます。"
    },
    "ネイリスト / アイリスト（まつ毛エクステ）": {
        "mbti_fit": ["ISTP", "ISFP", "INTJ", "INTP"],
        "traits": ["超精密な細部へのこだわり", "集中力・職人肌", "デザインの色彩感覚", "個性の表現"],
        "desc": "爪や目元という数ミリ単位のキャンバスに、精密な技術とデザインセンスで美を宿すプロフェッショナル。",
        "strengths_match": "細かい手作業や没頭する作業が好きで、自分の世界観やトレンドカラーを表現したい人に最適です。",
        "growth_path": "画像解析AI等で左右対称バランスを客観チェックし、細部へのこだわりを徹底的に磨きます。"
    },
    "美容企画・プレス / ビューティインフルエンサー": {
        "mbti_fit": ["ENTP", "ENFP", "ENTJ", "ESTP"],
        "traits": ["トレンド分析・SNS発信", "企画立案力", "マーケティング視点", "表現力・発信力"],
        "desc": "新しい美容ブームやブランドの魅力を世の中に発信し、プロダクトや情報を企画・プロデュースする仕事。",
        "strengths_match": "SNSでの発信や新しいトレンド・コスメの分析が好きで、アイデアを形にするのが得意な人にぴったりです。",
        "growth_path": "生成AIを活用した市場分析・コンテンツ試作を学び、ポートフォリオで発信力を証明します。"
    }
}

# ==========================================
# Tab 1: 適性診断入力フォーム
# ==========================================
with tab1:
    st.header("📝 個別適性診断チェックシート")
    st.markdown("以下の4つのエリア（MBTI・対人スタイル・好きなこと・苦手なこと）に回答することで、あなたの強みが生きる美容職種をAIが判定します。")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("1. 性格タイプ（MBTI傾向）")
        mbti_e_i = st.radio("エネルギーの方向", ["E型 (外向的・人と会うと元気が出る)", "I型 (内向的・1人で没頭すると充実する)"], index=0)
        mbti_s_n = st.radio("情報の取り込み方", ["S型 (現実的・五感や事実を重視)", "N型 (直感的・アイデアや未来の可能性を重視)"], index=0)
        mbti_t_f = st.radio("判断の基準", ["T型 (論理的・客観的な理由を重視)", "F型 (感情的・人への共感や調和を重視)"], index=1)
        mbti_j_p = st.radio("行動のスタイル", ["J型 (計画的・スケジュール通り進めたい)", "P型 (柔軟・その場の流れや変化を楽しみたい)"], index=1)
        
        # MBTIコード生成
        mbti_code = f"{mbti_e_i[0]}{mbti_s_n[0]}{mbti_t_f[0]}{mbti_j_p[0]}"
        st.info(f"あなたの推定MBTIタイプ: **{mbti_code}**")

        st.subheader("2. 対人スタイル・社会性")
        social_style = st.selectbox(
            "あなたが最も心地よい接客・人間関係のスタイルは？",
            [
                "1対1で深くお客様の悩みに寄り添いたい（深耕型）",
                "明るく賑やかに多くの人を楽しませたい（ムードメーカー型）",
                "裏方として徹底的に相手をサポートし、喜ばせたい（ホスピタリティ型）",
                "自分の知識やトレンドを論理的に解説・提案したい（アドバイザー型）",
                "静かに自分の作品や手技に没頭し、結果で示したい（職人型）"
            ]
        )

    with col_b:
        st.subheader("3. 好きなこと・得意なこと（複数選択可）")
        likes = st.multiselect(
            "興味がある・ワクワクすることを選択してください：",
            [
                "髪のスタイリングやアレンジ・カラーリング",
                "メイクアップ・パーソナルカラーの分析",
                "スキンケア・肌質改善・マッサージ",
                "ネイルアート・細かい手仕事・クラフト",
                "トレンドのSNSチェック・写真撮影・動画編集",
                "人の話を聞くこと・悩み相談に乗ること",
                "最新コスメの成分チェック・効果の分析"
            ],
            default=["髪のスタイリングやアレンジ・カラーリング", "人の話を聞くこと・悩み相談に乗ること"]
        )

        st.subheader("4. 苦手なこと・避けたい環境")
        dislikes = st.multiselect(
            "できれば避けたい・苦手だと感じることを選択してください：",
            [
                "大勢の前でのスピーチや目立つこと",
                "長時間じっと座り続けること（立ち仕事は平気）",
                "数値管理や複雑な事務書類の作成",
                "人との会話が少ない孤独な作業",
                "急なスケジュール変更やルールがない状態",
                "細かい手作業やミリ単位の作業"
            ],
            default=["数値管理や複雑な事務書類の作成"]
        )

    st.markdown("---")
    submit_diag = st.button("✨ 適性を分析しておすすめ職種 TOP 3 を表示する", type="primary")

# ==========================================
# Tab 2 & 3: 診断結果およびアドバイス
# ==========================================
if submit_diag or "diag_run" in st.session_state:
    st.session_state["diag_run"] = True
    
    # スコアリングロジック
    scores = {}
    for career_name, info in CAREER_DATABASE.items():
        score = 50  # ベーススコア
        
        # MBTIマッチ度
        if mbti_code in info["mbti_fit"]:
            score += 25
        elif mbti_code[0] == info["mbti_fit"][0][0]: # 先頭文字一致
            score += 10
            
        # 好きなこととのマッチング
        if "美容師" in career_name and "髪のスタイリングやアレンジ・カラーリング" in likes:
            score += 20
        if "ヘアメイク" in career_name and "メイクアップ・パーソナルカラーの分析" in likes:
            score += 20
        if "ビューティアドバイザー" in career_name and ("スキンケア・肌質改善・マッサージ" in likes or "人の話を聞くこと・悩み相談に乗ること" in likes):
            score += 20
        if "エステ" in career_name and "スキンケア・肌質改善・マッサージ" in likes:
            score += 20
        if "ネイル" in career_name and "ネイルアート・細かい手仕事・クラフト" in likes:
            score += 20
        if "企画" in career_name and "トレンドのSNSチェック・写真撮影・動画編集" in likes:
            score += 20

        # 苦手なことによる補正
        if "細かい手作業やミリ単位の作業" in dislikes and "ネイル" in career_name:
            score -= 25
        if "大勢の前でのスピーチや目立つこと" in dislikes and "企画" in career_name:
            score -= 15

        scores[career_name] = min(score, 98) # 最大98%

    # スコア順にソートしてTOP 3抽出
    sorted_careers = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]

    with tab2:
        st.header("🎯 診断結果：あなたに適した美容職種 TOP 3")
        st.markdown(f"**{student_name} 様**（タイプ: `{mbti_code}`）の診断結果です。上位3つの適性職種を提案します。")
        
        rank_medals = ["🥇 第1位", "🥈 第2位", "🥉 第3位"]
        
        for i, (c_name, match_rate) in enumerate(sorted_careers):
            c_info = CAREER_DATABASE[c_name]
            
            with st.expander(f"{rank_medals[i]}：{c_name}（適合率: {match_rate}%）", expanded=(i==0)):
                col_r1, col_r2 = st.columns([2, 1])
                
                with col_r1:
                    st.subheader(c_name)
                    st.write(f"**概要**: {c_info['desc']}")
                    st.write(f"**適性理由**: {c_info['strengths_match']}")
                    st.write(f"**求められる特性**: {', '.join(c_info['traits'])}")
                
                with col_r2:
                    st.metric("マッチ度", f"{match_rate}%", delta="ベストマッチ" if i==0 else "高適性")
                    st.caption(f"推奨MBTI: {', '.join(c_info['mbti_fit'])}")

                st.markdown("---")
                st.markdown(f"**🏫 滋慶学園での成長ステップ**: {c_info['growth_path']}")

    with tab3:
        st.header("👩‍🏫 教員用 1on1 面談ガイド & 成長ロードマップ")
        st.markdown("「③ひとり一人を見てゆく視点」に基づき、教員が面談や実技指導で活用できる個別の伴走ガイドです。")

        top1_name, top1_score = sorted_careers[0]
        top1_info = CAREER_DATABASE[top1_name]

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("💡 面談での共感＆肯定アプローチ")
            st.success(f"""
**1. 強みの承認**
学生の性格傾向（{mbti_code}）と「{social_style[:15]}...」という接客姿勢を高く評価します。
第1適性の **「{top1_name}」** に対する潜在的な意欲を引き出す言葉がけを行ってください。

**2. 悩みや苦手への寄り添い**
苦手項目として挙げられた「{', '.join(dislikes)}」に対し、
「無理に克服するのではなく、工夫やデジタルツール（AI）で補えるから安心してください」と声かけし、不安を解消します。
            """)

        with col_g2:
            st.subheader("✂️ 実技授業・手元指導での伴走ポイント")
            st.warning(f"""
**1. 五感と技術の磨き込み**
{top1_info['growth_path']}

**2. 人間教育の軸（「今日も笑顔であいさつを」）**
技術面だけでなく、明るい挨拶やホスピタリティ（身構え・気構え・心構え）を、日々の実習での声かけを通じて定着させます。
            """)

        st.markdown("---")
        st.subheader("📅 5年後・10年後のキャリアロードマップ（例）")
        st.markdown(f"""
- **在学中（1〜2年）**: AIポートフォリオに作品・手技データを蓄積。就職DXで「{top1_name}」に強みを持つサロンと個別マッチング。
- **卒業5年後（近未来）**: 現場で指名多数のトップクリエイター・店長として活躍。後輩の指導にも「ひとり一人を見る視点」を発揮。
- **卒業10年後（未来）**: 滋慶学園の**生涯就職紹介システム**と連携し、独立開業やフリーランス、海外展開（国際教育）へ挑戦！
        """)

        # 診断書ダウンロード機能
        report_text = f"""========================================
滋慶学園グループ 美容キャリア適性診断レポート
========================================
日付: {datetime.date.today()}
学生名: {student_name} ({course_type})
MBTIタイプ: {mbti_code}

【診断結果 TOP 3】
1位: {sorted_careers[0][0]} (適合率: {sorted_careers[0][1]}%)
2位: {sorted_careers[1][0]} (適合率: {sorted_careers[1][1]}%)
3位: {sorted_careers[2][0]} (適合率: {sorted_careers[2][1]}%)

【教員用1on1指導ガイド】
- 共感ポイント: {mbti_code}の強みを活かし、{top1_name}への目標を具体化する。
- 人間教育方針: 挨拶・ホスピタリティ・「五感、創造。」の感覚を日常の実習で育む。
========================================
"""
        st.download_button(
            label="📥 診断レポート＆面談シートをダウンロード (.txt)",
            data=report_text,
            file_name=f"career_diagnostic_{student_name}_{datetime.date.today()}.txt",
            mime="text/plain"
        )
