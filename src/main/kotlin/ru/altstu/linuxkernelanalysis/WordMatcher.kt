package ru.altstu.linuxkernelanalysis

import edu.stanford.nlp.ling.CoreAnnotations
import edu.stanford.nlp.pipeline.StanfordCoreNLP
import me.tongfei.progressbar.ProgressBar
import java.lang.RuntimeException
import java.util.*
import kotlin.collections.HashMap

// TODO: нужно смотреть (отрабатывает не так, как нужно)
class WordMatcher(useTfIdf: Boolean) : MessageMatcher {
    class TokenInfo(
        var word: String,
        var count: Int,
        var documentCount: Int
    )

    var messages: MutableList<WordMessange> = mutableListOf()
    private val posFilter: Array<String> = arrayOf(
        "FW",
        "JJ",
        "JJR",
        "JJS",
        "NN",
        "NNS",
        "NNP",
        "NNPS",
    )
    private val wordCommonInfo = HashMap<String, TokenInfo>()

    private var documentCount = 0

    override fun closestMessage(newMessage: String): String =
        throw RuntimeException("Не используется тут")

    override fun addNewMessage(newMessage: String) {
        val props = Properties()
        props.setProperty("annotators", "tokenize, ssplit, pos, lemma")
        val pipeline = StanfordCoreNLP(props)
        val document = pipeline.process(newMessage)
        val sentences = document.get(CoreAnnotations.SentencesAnnotation::class.java)

        val words = sentences
            .map { it.get(CoreAnnotations.TokensAnnotation::class.java) }
            .flatten()
            .filter { it.get(CoreAnnotations.PartOfSpeechAnnotation::class.java) in this.posFilter }
            .map { it.get(CoreAnnotations.LemmaAnnotation::class.java) }

        val localWordCount = words.distinct().associateWith { word -> words.count { it == word } }
        documentCount++

        messages.add(WordMessange())
        for ((word, count) in localWordCount) {
            if (wordCommonInfo.contains(word)) {
                wordCommonInfo[word]?.let {
                    it.count += count
                    it.documentCount++
                }
            } else {
                wordCommonInfo[word] = TokenInfo(
                    word = word,
                    count = count,
                    documentCount = 1
                )
            }
            messages.last().tokens[wordCommonInfo[word]!!] = count.toDouble()
        }
    }

    override fun getResult(countClaster: Int): List<IMessange> {
        WordMessange.countDocument = documentCount

        val clusterization = Clusterization(messages, messages.count()/50)
        var bestResult = clusterization.getResult()
        //var bestMetrik = clusterization.calculateSilhouetteCoefficient()
//
//
        //while (clusterization.clusterNumber != 1){
        //    progressBar.step()
        //    clusterization.clusterNumber--
        //    val curResult = clusterization.getResult()
        //    val curMetrik =  clusterization.calculateSilhouetteCoefficient()
        //    if(bestMetrik < curMetrik){
        //        bestResult = curResult
        //        bestMetrik = curMetrik
        //    }
        //}

        return bestResult
    }
}