from fastapi import FastAPI, UploadFile, File, HTTPException
from service import utils
from fastapi.middleware.cors import CORSMiddleware
import json
import uvicorn
import os
from service.src.modules.parser.v1.parser import Parser
from datetime import datetime
from core.schemas import schema
from service.src.modules.search_engine.v1.entity_search import EntityExtractor

app = FastAPI()
origins = ["*"]

with open(os.path.join('config.json'), 'r') as f:
    CONFIG = json.load(f)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

segmenter = utils.load_model(CONFIG)


@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    pdf_file = await file.read()

    today = datetime.today()
    passages, entities, block_types = utils.extract_passages(pdf_file, segmentation_model=segmenter)

    parser = Parser()
    parser.parse(passages, entities, block_types)

    output_dict = parser.convert_to_dict()

    passages_output = []
    for index, passage in enumerate(passages):
        passages_output.append({
            "block_id": index,
            "header": passage[1],
            "content": passage[0]
        })

    return {
        "date": today.strftime("%d-%m-%Y"),
        "status": "success",
        "data": {
            "passage_block": passages_output,
            "resume_information": output_dict
        }
    }


@app.post("/segmentation")
async def segmentation(segmentation_input: schema.SegmentationInput):
    passages = []
    try:
        processed_headings = ['work',
                              'workexperience',
                              'workingexperience',
                              'workhistory',
                              'experience',
                              'employment',
                              'history',
                              'career',
                              'project',
                              "education",
                              "academic"]

        passage, types = segmenter.segment(segmentation_input.text, 'experience',
                                           ['experience', 'education', 'project'])
        for j in range(len(passage)):
            if passage[j] != '':
                passages.append((passage[j], types[0]))

        entities_list = []

        for passage in passages:
            text = passage[0]
            heading = passage[1]
            only_text_heading = ''.join([e for e in heading if e.isalpha()])
            if any([e for e in processed_headings if e in only_text_heading.lower()]):
                entities_list += EntityExtractor.extract_entities(text.replace(" .", ". "), heading='EXPERIENCE')

        passages = segmenter.merge_segments(passages, processed_headings, entities_list, EntityExtractor)
    except:
        raise HTTPException(status_code=404, detail="System not available")

    return schema.SegmentationResponse(
        processed_date=datetime.today(),
        processed_type=segmentation_input.dataset,
        passages= [e[0] for e in passages]
    )


if __name__ == "__main__":
    uvicorn.run("__main__:app", host=CONFIG['DEPLOYMENT']['HOST'], port=int(CONFIG['DEPLOYMENT']['PORT']), reload=True)
