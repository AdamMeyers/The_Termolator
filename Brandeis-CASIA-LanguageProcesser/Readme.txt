This README file explains how to use the tool for Chinese word segmentation and POS tagging which is developed by the Chinese Language Processing Group, Brandeis University.

Contributors: Zhiguo Wang, Si Li, Nianwen Xue

Requirements
=============
Java version 1.8 or above



Usage
======

Use the following command:
java -Xmx25000m -cp "./WS_POS_brandeis.jar" brandeis.transition.wordseg.WordSegmentToolkit -mode test -model model/train_brandeis.model.gz -test INPUT_DIR -out OUTPUT_DIR

Example:
java -Xmx25000m -cp "./WS_POS_brandeis.jar" brandeis.transition.wordseg.WordSegmentToolkit -mode test -model model/train_brandeis.model.gz -test data -out output

If only test single file, the command is using ¡®ftest¡¯ as follows:
java -Xmx25000m -cp "./WS_POS_brandeis.jar" brandeis.transition.wordseg.WordSegmentToolkit -mode ftest -model model/train_brandeis.model.gz -ftest INPUT_File_DIR -out OUTPUT_File_DIR


DISCLAIMER:

The Authors makes no representations or warranties about the suitability of the Software, either express or implied, including but not limited to the implied warranties of merchantability, fitness for a particular purpose, or non-infringement. The Authors shall not be liable for any damages suffered by Licensee as a result of using, modifying or distributing the Software or its derivatives.
