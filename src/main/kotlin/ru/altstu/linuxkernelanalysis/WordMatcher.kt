package ru.altstu.linuxkernelanalysis

import edu.stanford.nlp.ling.CoreAnnotations
import edu.stanford.nlp.pipeline.StanfordCoreNLP
import java.lang.RuntimeException
import java.util.*
import kotlin.collections.HashMap
import kotlin.math.sqrt

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

    class MessageInfo{
        var words: MutableMap<TokenInfo, Int> = hashMapOf()
        // TODO возможно убрать
        var weight = 0.0
    }

    private var messages: MutableList<String> = arrayListOf()


    private val tfIdf = useTfIdf
    private val posFilter: Array<String> = arrayOf("SYM", "RP", "CC", "DT", "HYPH", ",", ".", ";")

    private val wordCommonInfo = HashMap<String, TokenInfo>()
    private val messagesInfo : MutableList<MessageInfo> = mutableListOf()
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
            .filter { it.get(CoreAnnotations.PartOfSpeechAnnotation::class.java) !in this.posFilter }
            .map { it.get(CoreAnnotations.LemmaAnnotation::class.java) }

        val localWordCount = words.distinct().associateWith { word -> words.count { it == word } }
        documentCount++

        messagesInfo.add(MessageInfo())
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
            messagesInfo.last().words[wordCommonInfo[word]!!] = count
        }
    }
    fun countDistance(firstMsg: MutableMap<TokenInfo, Int>, secondMsg: MutableMap<TokenInfo, Int>): Double {
        val compareWords = firstMsg + secondMsg
        var diff = 0.0

        for ((word, _) in compareWords) {
            val p1 = if (firstMsg.containsKey(word)) 1.0 else 0.0
            val p2 = if (secondMsg.containsKey(word)) 1.0 else 0.0
            diff += (p1 - p2) * (p1 - p2)
        }

        return sqrt(diff)
    }

    fun isNeighbours(firstMsg: MutableMap<TokenInfo, Int>, secondMsg: MutableMap<TokenInfo, Int>): Boolean {
        return countDistance(firstMsg, secondMsg) > neighborsDistance
    }

    override fun buildMessageDistances(): MutableList<MutableList<String>> {
        // iteration for all messages should be parallelized
        val cores = Runtime.getRuntime().availableProcessors()
        val threads = Vector<Thread>(cores)

        // TODO переделать нормально на классы - CLASTERIZATION
        val clusters: MutableList<Cluster> = mutableListOf()
        var clusterNum = 10


        for (i in messagesInfo.indices) {
            for (j in i + 1 until messagesInfo.size){
                val distance = countDistance(messagesInfo[i].words, messagesInfo[j].words)
                println("$distance between $i and $j")
            }
        }

        return messagesInfo
            .sortedBy { it.weight }
            .map { it.words }
            .map {
                it.keys
                    .map { it.word }
                    .toMutableList()
            }
            .toMutableList()
    }
}