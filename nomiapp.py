from flask import Flask, render_template, request, session
import re
import os
import base64
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # セッションの暗号化に使用するキー


@app.route("/", methods=["GET", "POST"])
def start():
    return render_template("start.html")


@app.route("/load", methods=["GET", "POST"])
def load():
    x = request.form.get("x")
    return render_template("load.html", x=x)


@app.route("/load2", methods=["GET", "POST"])
def load2():
    x = request.args.get("x")
    times = request.args.get("times")
    return render_template("load2.html", x=x, times=times)


@app.route("/meisi", methods=["GET", "POST"])
def meisi():
    return render_template("meisi.html")


@app.route("/nrec", methods=["GET", "POST"])
def nrec():
    x = request.args.get("x")

    store_cross_detail = pd.read_csv("store_cross_detail_retu2.csv")

    store_cross_detail = store_cross_detail.sort_values(
        ["id_x", "avg_cos_sim_rate"], ascending=[True, False]
    )
    df_sim_x = store_cross_detail[store_cross_detail["お酒の名前_x"].str.contains(x)]
    df_sim_x.reset_index(drop=True)

    def min_max(x, axis=None):
        min = x.min(axis=axis, keepdims=True)
        max = x.max(axis=axis, keepdims=True)
        result = (x - min) / (max - min)
        return result

    b = df_sim_x["avg_cos_sim_rate"]
    c = min_max(b.values)
    df_sim_x.insert(7, "正規化", c)
    # 一番上の日本酒を抽出して出力

    nyuryoku = df_sim_x.iloc[0]["お酒の名前_x"]
    nihonshu = df_sim_x.iloc[0]["お酒の名前_y"]
    key = df_sim_x.iloc[0]["texts_tfidf_sorted_top20_y"]

    return render_template(
        "nrec.html", nihonshu=nihonshu, times=0, x=x, key=key, nyuryoku=nyuryoku
    )


@app.route("/next_nihonshu", methods=["GET", "POST"])
def next_nihonshu():
    x = request.args.get("x")
    times = request.args.get("times")

    store_cross_detail = pd.read_csv("store_cross_detail_retu2.csv")

    store_cross_detail = store_cross_detail.sort_values(
        ["id_x", "avg_cos_sim_rate"], ascending=[True, False]
    )
    df_sim_x = store_cross_detail[store_cross_detail["お酒の名前_x"].str.contains(x)]
    df_sim_x.reset_index(drop=True)

    def min_max(x, axis=None):
        min = x.min(axis=axis, keepdims=True)
        max = x.max(axis=axis, keepdims=True)
        result = (x - min) / (max - min)
        return result

    b = df_sim_x["avg_cos_sim_rate"]
    c = min_max(b.values)
    df_sim_x.insert(7, "正規化", c)
    # 一番上の日本酒を抽出して出力

    times = int(times) + 1
    next_nyuryoku = df_sim_x.iloc[times]["お酒の名前_x"]
    next_selected_nihonshu = df_sim_x.iloc[times]["お酒の名前_y"]
    next_key = df_sim_x.iloc[times]["texts_tfidf_sorted_top20_y"]

    return render_template(
        "next_nihonshu.html",
        next_selected_nihonshu=next_selected_nihonshu,
        times=times,
        x=x,
        next_key=next_key,
        next_nyuryoku=next_nyuryoku,
    )


@app.route("/nihon", methods=["GET", "POST"])
def nihon():
    return render_template("nihon.html")


@app.route("/kmeisi", methods=["GET", "POST"])
def kmeisi():
    name = request.form.get("name")
    nick = request.form.get("nick")
    strong = request.form.get("strong")
    like = request.form.get("like")
    hate = request.form.get("hate")
    shasin = request.files["shasin"]  # アップロードされたファイルを取得

    content_type = ""  # ファイル形式を取得
    if "png" in shasin.content_type:
        content_type = "png"
    elif "jpeg" in shasin.content_type:
        content_type = "jpeg"

    # bytesファイルのデータをbase64にエンコードする
    uploadimage_base64 = base64.b64encode(shasin.stream.read())

    # base64形式のデータを文字列に変換する。その際に、「b'」と「'」の文字列を除去する
    uploadimage_base64_string = re.sub("b'|'", "", str(uploadimage_base64))

    # 「data:image/png;base64,xxxxx」の形式にする
    filebinary = f"data:image/{content_type};base64,{uploadimage_base64_string}"

    return render_template(
        "kmeisi.html",
        name=name,
        nick=nick,
        strong=strong,
        like=like,
        hate=hate,
        filebinary=filebinary,
    )


@app.route("/top", methods=["GET", "POST"])
def top():
    return render_template("top.html")


@app.route("/second", methods=["GET", "POST"])
def second():
    goal = request.form.get("goal")
    now = request.form.get("now")
    pace = request.form.get("pace")
    # goal_re = re.sub(r"\D", "", goal)
    # now_re = re.sub(r"\D", "", now)
    # pace_re = re.sub(r".$", "", re.sub(r"^.", "", pace))
    sex = request.form.get("sex")
    age = request.form.get("age")
    sweet = int(request.form.get("sweet"))
    bitter = int(request.form.get("bitter"))
    scent = int(request.form.get("scent"))
    acid = int(request.form.get("acid"))
    plain = int(request.form.get("plain"))
    fruity = int(request.form.get("fruity"))
    spark = int(request.form.get("spark"))

    HP = int(goal) - int(now)
    if pace == "早く":
        rec = HP / 1.5
    elif pace == "普通に":
        rec = HP / 3
    elif pace == "ゆっくり":
        rec = HP / 4
    else:
        rec = 999

    if rec <= 0:
        ans = 6
    elif rec <= 10:
        ans = 5
    elif rec <= 20:
        ans = 4
    elif rec <= 30:
        ans = 3
    elif rec <= 45:
        ans = 2
    elif rec <= 70:
        ans = 1
    else:
        ans = 0

    if sweet - 50 < 0:
        sweet_a = "0"
    else:
        sweet_a = "1"

    if bitter - 50 < 0:
        bitter_a = "0"
    else:
        bitter_a = "1"

    if scent - 50 < 0:
        scent_a = "0"
    else:
        scent_a = "1"

    if acid - 50 < 0:
        acid_a = "0"
    else:
        acid_a = "1"

    if plain - 50 < 0:
        plain_a = "0"
    else:
        plain_a = "1"

    if fruity - 50 < 0:
        fruity_a = "0"
    else:
        fruity_a = "1"

    if spark - 50 < 0:
        spark_a = "0"
    else:
        spark_a = "1"

    moji = sweet_a + bitter_a + scent_a + acid_a + plain_a + fruity_a + spark_a

    df = pd.read_csv("好みとアルコール.csv")

    # 類似度を計算する関数
    def calculate_similarity(query, string):
        return sum(q == s for q, s in zip(query, string))

    # 好みの類似度を計算してデータフレームを並び替え
    df["類似度"] = df["好み"].apply(lambda x: calculate_similarity(moji, x))
    df_konomi = df.sort_values(by="類似度", ascending=False).drop(columns="類似度")

    # アルコール量で区分0
    df_konomi_alcohol = df_konomi[df_konomi["アルコール"] >= ans].sort_values(by="アルコール")

    # 一番上の飲み物を抽出して出力
    drink = df_konomi_alcohol.iloc[0]["飲み物"]

    print(df_konomi_alcohol)

    return render_template(
        "second.html",
        drink=drink,
        ans=ans,
        goal=goal,
        now=now,
        pace=pace,
        sweet=sweet,
        bitter=bitter,
        scent=scent,
        acid=acid,
        plain=plain,
        fruity=fruity,
        spark=spark,
        times=0,
    )


@app.route("/next_drink", methods=["GET", "POST"])
def next_drink():
    drink_name = request.args.get("drink_name")
    goal = request.args.get("goal")
    now = request.args.get("now")
    pace = request.args.get("pace")
    sweet = request.args.get("sweet")
    bitter = request.args.get("bitter")
    scent = request.args.get("scent")
    acid = request.args.get("acid")
    plain = request.args.get("plain")
    fruity = request.args.get("fruity")
    spark = request.args.get("spark")
    times = request.args.get("times")

    HP = int(goal) - int(now)
    if pace == "早く":
        rec = HP / 1.5
    elif pace == "普通に":
        rec = HP / 3
    elif pace == "ゆっくり":
        rec = HP / 4
    else:
        rec = 999

    if rec <= 0:
        ans = 6
    elif rec <= 10:
        ans = 5
    elif rec <= 20:
        ans = 4
    elif rec <= 30:
        ans = 3
    elif rec <= 45:
        ans = 2
    elif rec <= 70:
        ans = 1
    else:
        ans = 0

    if int(sweet) - 50 < 0:
        sweet_a = "0"
    else:
        sweet_a = "1"

    if int(bitter) - 50 < 0:
        bitter_a = "0"
    else:
        bitter_a = "1"

    if int(scent) - 50 < 0:
        scent_a = "0"
    else:
        scent_a = "1"

    if int(acid) - 50 < 0:
        acid_a = "0"
    else:
        acid_a = "1"

    if int(plain) - 50 < 0:
        plain_a = "0"
    else:
        plain_a = "1"

    if int(fruity) - 50 < 0:
        fruity_a = "0"
    else:
        fruity_a = "1"

    if int(spark) - 50 < 0:
        spark_a = "0"
    else:
        spark_a = "1"

    moji = sweet_a + bitter_a + scent_a + acid_a + plain_a + fruity_a + spark_a

    df = pd.read_csv("好みとアルコール.csv")

    # 類似度を計算する関数
    def calculate_similarity(query, string):
        return sum(q == s for q, s in zip(query, string))

    # 好みの類似度を計算してデータフレームを並び替え
    df["類似度"] = df["好み"].apply(lambda x: calculate_similarity(moji, x))
    df_konomi = df.sort_values(by="類似度", ascending=False).drop(columns="類似度")

    # アルコール量で区分0
    df_konomi_alcohol = df_konomi[df_konomi["アルコール"] >= ans].sort_values(by="アルコール")

    # # 既に選ばれた飲み物の数をカウント
    # selected_drinks_count = session.get("selected_drinks_count", 0)

    # # 次に表示する飲み物を選択
    # next_selected_drink = df_konomi_alcohol.iloc[selected_drinks_count + 1]["飲み物"]

    # # 選択された飲み物の数を更新
    # session["selected_drinks_count"] = selected_drinks_count + 1

    times = int(times) + 1
    next_selected_drink = df_konomi_alcohol.iloc[times]["飲み物"]

    return render_template(
        "next_drink.html",
        # selected_drink=drink_name,
        next_selected_drink=next_selected_drink,
        ans=ans,
        times=times,
        goal=goal,
        now=now,
        pace=pace,
        sweet=sweet,
        bitter=bitter,
        scent=scent,
        acid=acid,
        plain=plain,
        fruity=fruity,
        spark=spark,
    )


if __name__ == "__main__":
    app.run()
