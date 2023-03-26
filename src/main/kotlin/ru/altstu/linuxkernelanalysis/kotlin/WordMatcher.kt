package ru.altstu.linuxkernelanalysis.kotlin

import edu.stanford.nlp.ling.CoreAnnotations
import edu.stanford.nlp.pipeline.StanfordCoreNLP
import java.lang.RuntimeException
import java.util.*
import java.util.concurrent.atomic.AtomicIntegerArray
import kotlin.collections.HashMap

// TODO: нужен рефактор после генерации
class WordMatcher(useTfIdf: Boolean) : MessageMatcher {
    data class TokenInforamtion(var word:String, var Count: Int, var AvgTF: Double, var DocumentCount: Int) {
        val SummOfTF: Double
            get() = AvgTF * DocumentCount
    }

    class MessangeInfo{
        var words =  HashMap<TokenInforamtion, Int>()
        var weight = 0.0
    }


    var messages: MutableList<String> = ArrayList()


    private val TfIdf = useTfIdf
    private val PosFlter = arrayOf("SYM", "RP", "CC", "DT", "HYPH", ",", ".", ";")

    private val WordCommonInforamtion = HashMap<String, TokenInforamtion>()
    private val MessangeInforamtion : MutableList<MessangeInfo> = mutableListOf()
    private val neighborsDistance = 0.7

    private var DocumentCount = 0

    override fun closestMessage(newMessage: String): String =
        throw RuntimeException("Не используется тут")


    override fun addNewMessage(newMessage: String) {
        val props = Properties()
        props.setProperty("annotators", "tokenize, ssplit, pos, lemma")
        val pipeline = StanfordCoreNLP(props)
        val document = pipeline.process(newMessage)
        val sentences = document.get(CoreAnnotations.SentencesAnnotation::class.java)

        val words = sentences.map { sentence ->
            sentence.get(CoreAnnotations.TokensAnnotation::class.java)
        }.flatten().filter { token -> token.get(CoreAnnotations.PartOfSpeechAnnotation::class.java) !in this.PosFlter }
            .map { token -> token.get(CoreAnnotations.LemmaAnnotation::class.java) }

        val localWordCount = words.distinct().associateWith { word -> words.count { w -> w == word } }
        DocumentCount++


        MessangeInforamtion.add(MessangeInfo())
        for ((word, count) in localWordCount) {
            if (WordCommonInforamtion.contains(word)) {
                WordCommonInforamtion[word]!!.Count += count
                WordCommonInforamtion[word]!!.AvgTF += (WordCommonInforamtion[word]!!.SummOfTF + count.toDouble() / words.size) /
                        (WordCommonInforamtion[word]!!.DocumentCount + 1)
                WordCommonInforamtion[word]!!.DocumentCount++
            } else {
                WordCommonInforamtion[word] = TokenInforamtion(word,count,count.toDouble()/words.size, 1)
            }
            MessangeInforamtion.last().words[WordCommonInforamtion[word]!!] = count
        }
    }
    fun countDistance(messange1: HashMap<TokenInforamtion, Int>, messange2: HashMap<TokenInforamtion, Int>):Double{
        val compareWords = messange1 + messange2
        var diff = 0.0

        for ((word, count) in compareWords) {
            val p1 = if (messange1.containsKey(word)) 1.0 else 0.0
            val p2 = if (messange2.containsKey(word)) 1.0 else 0.0
            diff += (p1 - p2) * (p1 - p2)
        }

        return Math.sqrt(diff)
    }

    fun isТeighbors(messange1: HashMap<TokenInforamtion, Int>, messange2: HashMap<TokenInforamtion, Int>):Boolean{
        return countDistance(messange1, messange2) > neighborsDistance
    }



    @Throws(InterruptedException::class)
    override fun buildMessageDistances():MutableList<MutableList<String>> {
        val ws = Any()
        // iteration for all messages should be parallelized
        val cores = Runtime.getRuntime().availableProcessors()
        val msgLen = messages.size
        val threads = Vector<Thread>(cores)


        for (i in MessangeInforamtion.indices){
            for (j in i + 1 until MessangeInforamtion.size){
                val distance = countDistance(MessangeInforamtion[i].words, MessangeInforamtion[j].words)
                println("${distance} between ${i} and ${j}")
            }
        }


        return MessangeInforamtion.sortedBy{it.weight}.map{it.words}.map { it.keys.map { it.word }.toMutableList()}.toMutableList()
    }
}