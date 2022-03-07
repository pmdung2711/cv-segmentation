from service.src.modules.segmentation.v1.TextSegmenter import TextSegmenter
from service.src.modules.textextraction.v1.TextExtractor import  TextExtractor
from service.src.modules.search_engine.v1.entity_search import EntityExtractor
CONFIG = {
    "SEGMENTATION":
        {
            "SEGMENT_MODEL": "models/segmentation/lite_v3.h5",
            "TFHUB_MODEL": "models/tfhub/sentence_encoder",
            "MAX_SENTENCES": "128"
        },

}

def extract_passages(pdf_file, segmentation_model, heading_patterns = None):

    texts, headings, label = TextExtractor.get_text(pdf_file=pdf_file)

    passages = []

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


    for i in range(len(texts)):
        passage, types = segmentation_model.segment(texts[i], headings[i], processed_headings)
        for j in range(len(passage)):
            if passage[j] != '':
                passages.append((passage[j], types[j]))

    entities_list = []

    for passage in passages:
        heading = passage[1]
        text = passage[0]
        only_text_heading = ''.join([e for e in heading if e.isalpha()])
        if any([e for e in processed_headings if e in only_text_heading.lower()]):
            entities_list += EntityExtractor.extract_entities(text.replace(" .", ". "), heading='EXPERIENCE')

    passages = TextSegmenter.merge_segments(passages, processed_headings, entities_list, EntityExtractor)

    entities = []
    block_types = []
    for i in range(len(passages)):
        passage_entities, block_type = EntityExtractor.extract(passages[i], entities_list)
        entities.append(passage_entities)
        block_types.append(block_type)

    return passages, entities, block_types


def load_model(config):
    segmentation_model = TextSegmenter(model_weights=config['SEGMENTATION']['SEGMENT_MODEL'],
                                      tf_hub_path=config['SEGMENTATION']["TFHUB_MODEL"],
                              max_sentences=int(config['SEGMENTATION']['MAX_SENTENCES']))

    return segmentation_model


if __name__ == "__main__":
    segmenter = load_model(CONFIG)
