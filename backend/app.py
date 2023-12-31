#No of endpoints required:-

#Get text and return the query result

#Get image and get the query result

#Make two endpoints for the above two tasks using flask
import flask
from flask import request, jsonify
from PIL import Image
from io import BytesIO
import base64
import weaviate
from transformers import CLIPProcessor, CLIPModel
import helper as h
from flask_cors import CORS


app = flask.Flask(__name__)
CORS(app )

keyword_dict = {
	"Harry" : "Mens",
	"Hermione" : "Girls",
	"Ron" : "Mens",
	"Ginny" : "Girls",
}

model_dict = {
	"Harry" : "Male",
	"Hermione" : "Female",
	"Ron" : "Male",
	"Ginny" : "Female",
}

profile_dict = {
	"Harry" : "Male Profile 1",
	"Hermione" : "Female Profile 1",
	"Ron" : "Male Profile 2",
	"Ginny" : "Female Profile 2",
}

@app.route('/query', methods=['POST'])
def getQuery():
	query = request.json['query']
	profile = request.json['profile']

	keyword = keyword_dict[profile]
	profile_id = profile_dict[profile]

	

	embedding = h.getTextEmbeddings(query)
	top_embedding , bottom_embedding = h.getTopAndBottomEmbeddings(embedding , keyword)
	top_products = h.getProducts(top_embedding, keyword, "Tops")
	bottom_products = h.getProducts(bottom_embedding, keyword, "Bottoms")
	ranking_top = h.getRanking(embedding.tolist()[0] , top_products["data"]["Get"]["FlipkartCleanProducts"] , f"{profile_id} Top") 
	ranking_bottom = h.getRanking(embedding.tolist()[0] , bottom_products["data"]["Get"]["FlipkartCleanProducts"] , f"{profile_id} Bottom") 

	top3top  = []
	for key, value in ranking_top.items():
		try:
			if key == 3: break
			top3top.append(top_products["data"]["Get"]["FlipkartCleanProducts"][value])
			
		except:
			pass

	top3bottom  = []
	for key, value in ranking_top.items():
		try:
			if key == 3: break
			top3bottom.append(bottom_products["data"]["Get"]["FlipkartCleanProducts"][value])
			
		except:
			pass
	
	response = {
		"message" : "Here are some outfits for you!",
	}

	outfits = []
	gender = model_dict[profile]
	for i in range(min(len(top3bottom) , len(top3top))):
		top_title = top3top[i]["product"]
		bottom_title = top3bottom[i]["product"]
		top_color = top3top[i]["colour"]
		bottom_color = top3bottom[i]["colour"]
		outfit = {
			"prompt" : f"full-body potrait of {gender} model wearing {top_title} with colour {top_colour} and {bottom_title} with having {bottom_color}having white background day lighting 2k resolution",
			"top" : {"title" : top_title, "image" : top3top[i]["image"] , "price" : top3top[i]["price"] , "link" : top3top[i]["uRL"]},
			"bottom" : {"title" : bottom_title , "image" : top3bottom[i]["image"] , "price" : top3bottom[i]["price"] , "link" : top3bottom[i]["uRL"]}
		}
		outfits.append(outfit)

	response["outfits"] = outfits
	return jsonify(response)


@app.route('/image', methods=['GET'])
def getImage():
	image = request.json['image']

	return jsonify({'image': image, 'reply': "Here are some outfits for you!" , "components": [ 
		{
		"image": image,
		"price": 1000,
		"link": "https://www.amazon.in/",
		"title": "T-shirt",
		},

		{
		"title": "Jeans",
		"image": image,
		"price": 500,
		"link": "https://www.amazon.in/",
		},
	]})


if __name__ == '__main__':
	app.run(debug=True)
