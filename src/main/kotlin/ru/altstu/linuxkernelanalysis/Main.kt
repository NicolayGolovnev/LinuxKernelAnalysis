package ru.altstu.linuxkernelanalysis
import ru.altstu.linuxkernelanalysis.kotlin.WordMatcher
fun main(args: Array<String>) {
    val boopa = WordMatcher(true)

    println(boopa.addNewMessage("fixed fix boopa booping fixing fixes this me my them"))
}