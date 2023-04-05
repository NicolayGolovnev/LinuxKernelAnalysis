package ru.altstu.linuxkernelanalysis

fun main(args: Array<String>) {
    val boopa = WordMatcher(true)
        boopa.addNewMessage("fixed dore")
        boopa.addNewMessage("fixed core")
        boopa.addNewMessage("boopa")
        boopa.addNewMessage("loopa")
        boopa.addNewMessage("zoopa")
        boopa.addNewMessage("zoopa boopa")

    val result = boopa.getResult(5)
    for( r in result){
        println(r.toString())
    }


}