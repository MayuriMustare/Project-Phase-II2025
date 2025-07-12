from flask import Flask, render_template, request
from utils.recommender import user_df, product_df, recommend_for_user, get_recommendations, predict_related_products

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/relatedPR')
def related_products():
    return render_template('relatedPR.html', products=product_df["Name"].tolist())

@app.route('/associatedPR')
def associated_products():
    return render_template('associatedPR.html', products=product_df["Name"].tolist())

@app.route('/userBR')
def user_products():
    return render_template('userBR.html', users=user_df["Name"].tolist(),)



@app.route("/recommend_user", methods=["POST"])
def recommend_user():
    user_name = request.form.get("user").strip()
    matched_users = user_df[user_df["Name"].str.lower() == user_name.lower()]
    if matched_users.empty:
        return render_template("userBR.html", title="User Not Found", users=user_df["Name"].tolist(),
                               products=product_df["Name"].tolist(), error="User not found", selected_user=user_name)

    user_id = matched_users["User ID"].values[0]

    # Get recommended product IDs
    results = recommend_for_user(user_id)  # Should return DataFrame with at least 'Product ID'

    # Merge to get product names and brands
    results = results.merge(product_df[["Product ID", "Name", "Brand", "Quantity", "Price","SubCategory","Description"]], on="Product ID", how="left")
    return render_template("userBR.html", title=f"Recommendations for {user_name}",
                           results=results.to_dict(orient='records'),
                           users=user_df["Name"].tolist(),
                           products=product_df["Name"].tolist(),
                           selected_user=user_name)


@app.route("/recommend_product", methods=["POST"])
def recommend_product():
    product_name = request.form.get("similar_product").strip()
    matched_products = product_df[product_df["Name"].str.lower() == product_name.lower()]
    if matched_products.empty:
        return render_template("associatedPR.html", title="Product Not Found", users=user_df["Name"].tolist(),
                               products=product_df["Name"].tolist(), error="Product not found",
                               selected_similar_product=product_name)
    product_id = matched_products["Product ID"].values[0]
    results = get_recommendations(product_id)
    print(results)
    return render_template("associatedPR.html", title=f"Associated to {product_name}",
                           results=results.to_dict(orient='records'),
                           users=user_df["Name"].tolist(),
                           products=product_df["Name"].tolist(),
                           selected_similar_product=product_name)


@app.route("/related_category", methods=["POST"])
def related_category():
    product_name = request.form.get("category_product").strip()
    matched_products = product_df[product_df["Name"].str.lower() == product_name.lower()]
    if matched_products.empty:
        return render_template("relatedPR.html", title="Product Not Found",
                               users=user_df["Name"].tolist(),
                               products=product_df["Name"].tolist(),
                               error="Product not found",
                               selected_category_product=product_name)

    result_df = predict_related_products(product_name)
    print(result_df)
    return render_template("relatedPR.html", title=f"Related Products for {product_name}",
                           results=result_df[["Product ID", "Name", "Brand", "Quantity","Price","SubCategory","Description"]].to_dict(orient='records'),
                           users=user_df["Name"].tolist(),
                           products=product_df["Name"].tolist(),
                           selected_category_product=product_name)


@app.route("/details/<product_id>")
def product_details(product_id):
    product = product_df[product_df["Product ID"] == product_id].iloc[0]
    return render_template("details.html", product=product)

if __name__ == "__main__":
    app.run(debug=True)
