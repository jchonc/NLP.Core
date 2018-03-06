# Some Experiments around NLP

## History & Background

Natural Language Processing is one of the hot areas in recent years, especially after all the main stream machine learning / neural network algorithms started to be adopted to process the language. (i.e. CNN RNN LSTM) While [Standford CoreNLP](https://nlp.stanford.edu/) is still one of the top players, a lot of new libraries started to emerge, [NTLK](https://www.nltk.org/) and [SpaCy](https://spacy.io/) are among the top players, others are gensim, GloVe...etc. Aside from that, API based implementation also start to show, [Google Natural Language](https://cloud.google.com/natural-language/) and [Azure Text Analytics API](https://azure.microsoft.com/en-us/services/cognitive-services/text-analytics/) and [Aylien](https://aylien.com/text-analysis-platform/) are among the popular ones. On top of that, we finally started to see some real applications build from it, [x.ai Meeting Scheduler](x.ai) is one of it.

## Privacy & Security Concerns

Because of the privacy/security concerns, we are still not sure if passing PHI information through a public API structure (i.e. Google or Microsoft) is allowable. So we will just do keep an eye on them for now.

## Library of Interest

Among those libraries, SpaCy is an interesting one. It emphasizes a lot more on commercial production ready - it calls itself "Industrial-Strength" (vs. some others are a lot more academic focused).

The functionality we care the most for now are classifier and NER. The classifier will help us guess the classification or severity from a paragraph of free text and the NER will help us identify the person/location/date/time out of the free text to allow further information extraction. 

## Using SpaCy in real life

The code of this article can be found at [here](https://github.com/rlrnd/NLP.Core/). But the data is not for PHI reasons.

### Using historic data to train the classifier

We are extracting the top 3000 incident file, and using the description field and general incident classification and severity as the original training data. We noticed the tier number stopped helping after 7 thus we leaved it there. 

```
Load 4951 incidents
Using 2951 as training data, 999 as test data)
Training the model...
LOSS      P       R       F
928.308 0.748   0.019   0.036
581.201 0.711   0.024   0.047
435.476 0.702   0.026   0.049
341.327 0.684   0.027   0.052
276.818 0.679   0.028   0.054
228.734 0.672   0.028   0.055
202.960 0.668   0.029   0.055
Saved model to model
```

### Testing the accuracy

We have then continue to use the next 1000 records to verify the accuracy and the results are somewhat better than we thought. 

```
Good guess (top 3) on classification: 815  of  1000
Good guess (top 3) on severity: 738  of  1000
```

### Using a docker container to host SpaCy API. 
Due to the recent upgrade we can start to leverage Python stack in VisualStudio.NET environment now so it worked quite well in our case.  So a restful API was created using [Falcon](https://falconframework.org/) and wrapped with a simple docker container.

```
FROM python:latest
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt 
RUN python -m spacy download en_core_web_sm
EXPOSE 8000
CMD [ "python", "/app/app.py" ]
```

This container will expose on port 8000 and serve /ent and /cls for named entity recognition and classifier purpose. 

### Consume those APIs

From the C# web project, we can forward the incoming text to the SpaCy API and get 2 pieces of information back. First is the marked content of where the PERSON/DATE/LOCATION and 2nd is the likelyhood of the categories/severity. 

![Screenshot of submission](https://github.com/rlrnd/NLP.Core/raw/master/Submission.gui.png)

### Feedback link

If the first case handler is not happy with the result, he/she should manually mark the file and later those results can be send back to the SpaCy API for retraining. However, this process might be time consuming thus need to happen in batches. 

## Misc.

SpaCy can also been used to help de-identify the data to identify the person names, dates and location/organizations. But probably direct keyword search on MRN, DOB or License can happen before that.


