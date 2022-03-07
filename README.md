# cv-segmentation
University Final Project


# Model Download 

Drive : https://drive.google.com/drive/folders/1lXOUEPrF-mf93PpfiVWC5v5hYUBXD5MB?usp=sharing

Put the model in backend/service/src/models/segmentation
Put the tf_hub model in backend/service/src/models/tfhub

Change the config file as follow:

{
    "SEGMENTATION":
    {
        "SEGMENT_MODEL":"service/src/models/segmentation/[name of model]",
        "TFHUB_MODEL":"service/src/models/tfhub/sentence_encoder",
        "MAX_SENTENCES":"128"
    },

    "DEPLOYMENT":
    {
        "HOST":"0.0.0.0",
        "PORT":"8899"
    }
}