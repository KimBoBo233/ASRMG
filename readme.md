# ASRMG: Business Topic Clustering-based Architecture Smell Refactoring for Microservices Granularity 
# Introduce of this dataset
The repository provided 5 microservices systems with architectural granularity smells, stored by means of Excel.
The smells were determined by our expert team through the voting process and were used to support the analysis of our method "**ASRMG**" to refactor microservice
architecture granularity smells.

## Structure of this dataset
Each .xlsx file consists of three columns representing **the first column** means the of the microservice, 
**the second column means** full name of the interface, 
and **the third column means** whether or not there is an architectural granularity smell. For using this dataset,
you can download these .xlxs files and read them through file operate utils(such as **pandas**) in the program, and operate in the way
of operating Workbook.


## Introduce of experts
The number of smells in the table refers to the count of microservice architecture granularity smells, determined through a consensus reached by 5 experts after analyzing the microservice system code. We invited five experts in the field of intelligent software engineering, who are members of the China Computer Federation(CCF) Software Engineering Committee, specializing in the field of intelligent software engineering, and have extensive experience in microservice software quality.

1.**Xin Chen**: He presided over one National Natural Science Foundation project and one Provincial Natural Science Foundation project. Published over 40 papers, including IEEE/ACM Transactions (TSE, TR, TOIT), EMSE, SANER, ISSRE, IST, FCS, ASOC Computer Research and Development, and other well-known domestic and international journals and conferences.

2.**Jie Chen**: In 2016, she obtained a doctorate degree in computing software and theory from the Software Research Institute of the Chinese Academy of Sciences. Her main research interests include software engineering and big data analysis, involving data mining in the open source community, code quality analysis, etc.

3.**Bin Hu**: Participated in a project funded by the National Natural Science Foundation of China. Published two high-level international conference papers as the first author.

4.**Sixuan Wang**: He has served as the chief architect and technical consultant for multiple leading enterprises' digital transformation projects, covering various industries. He has years of experience in combining academic research with practical enterprise engineering and has rich experience in school-enterprise cooperation, student training, and the integration of government, industry, academia, and research.

5.**Dongjin Yu**: He has published more than 100 academic papers in SCI-indexed journals, first-class journals, and important international academic conferences, edited 5 monographs, and edited one textbook for the "Twelfth Five Year Plan" for outstanding engineers.

# Introduce of Experiments
This is the main code of ASRMG, among them, reconstruct_main.Py is for refactoring purposes, and evaluate_main.Py is for analysis purposes. RQ1 to RQ4 in this article **ASRMG** are based on the analyzed data.
## HOW TO USE
Before running **reconstruct_main.py**, it is necessary to modify the configuration file. Please change the path in **global_config.py**.

After running **reconstruct_main.py**, you just need to run **evaluate_main.py** to evaluate the result of **reconstruct_main.py**. 

The data obtained from evaluate_main.py is used to reproduce RQ1~RQ4 in the **Experiments/RQ** file of this article.

**RQ1**
includes a comparison of the scale, smell quantity, and various indicators of the system before and after refactoring.

**RQ2**
taking the BSA system as an example includes interval partitioning at different scales after system reconstruction, smell quantity, and indicators of SDH and SPH.

**RQ3**
includes a comparison of evaluation systems at different reconstruction scales and the similarity between reconstruction results and manual reconstruction.

**RQ4**
includes a comparison of various indicators with and without low fitness processing.





