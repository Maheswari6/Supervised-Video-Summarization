# Supervised-Video-Summarization

### Problem
We consider Video Summarization as supervised subset selection problem <br>
Formulate it as sequence to sequence learning problem, where the input is sequence of original video frames and output is a keyshot sequence

### Approach
* We use 2 models - Encoder Decoder model, Keyshot selection model <br>
* The encoder decoder architecture, built using Bi-LSTM and LSTM models, measures the importance of each frame <br>
* Keyshot selection model that converts frame level importance scores into short level importance scores <br>
* To minimize the number of generated keyshots, we rank the intervals based on the number of keyframes in intervals divided by their lengths, and finally apply knapsack algorithm to ensure that the produced keyshot-based summary is of maximum 15 percent in length of the original test video <br>
* From the shot-level importance scores, we can formulate video summarization as the 0/1 Knapsack Problem: given a time budget (e.g., 15 seconds), maximize the total importance score of the shots included in a summary. The solution will be a vector of size T (the number of frames in a video), whose values are either 0 (not in summary) or 1 (include in summary) <br>
* We calculate F1-score to determine how similar our generated video summary is to that of annotated summary

### Datasets Used
<b>SumMe :</b> 
The dataset consists of 25 videos which are single-shot and range in length from 1-6 minutes. The dataset contains summaries created by users with the constraint in length being that the summaries should be 5% to 15% of the original video. (Size: 2.2 GB) <br>
Link to the original dataset [here](https://gyglim.github.io/me/vsum/index.html)<br>
<b> TVSum : </b>
Title-based Video Summarization (TVSum) dataset serves as a benchmark to validate video summarization techniques. It contains 50 videos of various genres (e.g., news, how-to, documentary, vlog, egocentric) and 1,000 annotations of shot-level importance scores obtained via crowdsourcing (20 per video). <br>
Link to the original dataset [here](http://people.csail.mit.edu/yalesong/tvsum/)
