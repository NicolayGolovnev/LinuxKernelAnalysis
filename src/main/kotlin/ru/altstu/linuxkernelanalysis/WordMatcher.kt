package ru.altstu.linuxkernelanalysis

import edu.stanford.nlp.ling.CoreAnnotations
import edu.stanford.nlp.pipeline.StanfordCoreNLP
import java.lang.RuntimeException
import java.util.*
import kotlin.collections.HashMap

// TODO: нужно смотреть (отрабатывает не так, как нужно)
class WordMatcher(useTfIdf: Boolean) : MessageMatcher {
    class TokenInfo(
        var word: String,
        var count: Int,
        var avgTF: Double,
        var documentCount: Int
    ) {
        val sumOfTF: Double
            get() = avgTF * documentCount
    }

    var messages: MutableList<WordMessange> = mutableListOf()


    private val tfIdf = useTfIdf
    //private val posFilter: Array<String> = arrayOf("SYM", "RP", "CC", "DT", "HYPH", ",", ".", ";")
    private val posFilter: Array<String> = arrayOf(
        "FW",
        "JJ",
        "JJR",
        "JJS",
        "NN",
        "NNS",
        "NNP",
        "NNPS",
        "POS",
        "RB",
        "RBR",
        "RBS",
        "VB",
        "VBD",
        "VBG",
        "VBN",
        "VBP",
        "VBZ",
    )

    private val wordCommonInfo = HashMap<String, TokenInfo>()
    private val neighborsDistance = 0.7

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
            .filter { it != "fix" }

        val localWordCount = words.distinct().associateWith { word -> words.count { it == word } }
        documentCount++

        messages.add(WordMessange())
        for ((word, count) in localWordCount) {
            if (wordCommonInfo.contains(word)) {
                wordCommonInfo[word]?.let {
                    it.count += count
                    it.avgTF += (it.sumOfTF + count.toDouble() / words.size) / (it.documentCount + 1)
                    it.documentCount++
                }
            } else {
                wordCommonInfo[word] = TokenInfo(
                    word = word,
                    count = count,
                    avgTF = count.toDouble()/words.size,
                    documentCount = 1
                )
            }
            messages.last().tokens[wordCommonInfo[word]!!] = count.toDouble()
        }
    }

    override fun getResult(countClaster: Int): List<IMessange> {
        val clusterization = Clusterization(messages, countClaster)
        clusterization.execute()
        return clusterization.centroids
    }
}