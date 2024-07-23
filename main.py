import sys
from PIL import Image
from sentence_transformers import SentenceTransformer
import vecs
import os

DB_CONNECTION = os.getenv('DB_CONNECTION')
vx = vecs.create_client(DB_CONNECTION)
images = vx.get_collection(name="image_vectors")

# Load CLIP model
model = SentenceTransformer('clip-ViT-B-32')

def seed():
    # create vector store client
    vx = vecs.create_client(DB_CONNECTION)

    # create a collection of vectors with 512 dimensions
    images = vx.get_collection(name="image_vectors")

    # Load CLIP model
    model = SentenceTransformer('clip-ViT-B-32')

    import os
    vectors = []
    for image in os.listdir('flower_images') :
        image = f'./flower_images/{image}'
        img_emb = model.encode(Image.open(image))
        print(img_emb)
        vectors.append((
                image,       # the vector's identifier
                img_emb,        # the vector. list or np.array
                {"type": "jpg"}  # associated  metadata
            ))

    # add records to the *images* collection
    images.upsert(
        vectors=vectors
    )
    print("Inserted images")

    # index the collection for fast search performance
    images.create_index()
    print("Created index")


def search(query_string):
    # create vector store client
    vx = vecs.create_client(DB_CONNECTION)
    images = vx.get_collection(name="image_vectors")

    # Load CLIP model
    model = SentenceTransformer('clip-ViT-B-32')
    # Encode text query
    text_emb = model.encode(query_string)

    # query the collection filtering metadata for "type" = "jpg"
    results = images.query(
        query_vector=text_emb,              # required
        limit=10,                            # number of records to return
        # filters={"type": {"$eq": "jpg"}},   # metadata filters
    )

    return results



from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    images = []
    if request.method == 'POST':
        query_string = request.form['query']
        images = search(query_string)
        print(images)
    return render_template('index.html', images=images)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    

