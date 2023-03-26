package ru.altstu.linuxkernelanalysis
import ru.altstu.linuxkernelanalysis.kotlin.WordMatcher

fun main(args: Array<String>) {
    val boopa = WordMatcher(true)
    boopa.addNewMessage("fix")
    boopa.addNewMessage("fix")





    println(boopa.buildMessageDistances())
}