package ru.altstu.linuxkernelanalysis.kotlin

import org.eclipse.jgit.api.Git
import org.eclipse.jgit.diff.*
import org.eclipse.jgit.lib.Constants
import org.eclipse.jgit.lib.Repository
import org.eclipse.jgit.patch.FileHeader
import org.eclipse.jgit.revwalk.RevCommit
import org.eclipse.jgit.revwalk.RevWalk
import org.eclipse.jgit.util.io.DisabledOutputStream
import ru.altstu.linuxkernelanalysis.kotlin.SortUtil.sortByDescValue
import java.io.IOException
import java.util.*

class RepositoryScanner(matherType:MessageMatcher, rep: Repository, startDate: Date, endDate: Date) {
    private val repository:Repository = rep
    private val git:Git = Git(rep)
    private val Matcher: MessageMatcher = matherType
    private val StartDate = startDate
    private val EndDate = endDate

    var PathInGit:String? = null
    var MapFileChanges: MutableMap<KeyFilePos, Int> = HashMap()
    var MapFileNameChanges: MutableMap<String, Int> = HashMap()

    @Throws(IOException::class)
    fun detectChanges( parent: RevCommit, commit: RevCommit) {
        val diffFormatter = DiffFormatter(DisabledOutputStream.INSTANCE)
        diffFormatter.setRepository(repository)
        diffFormatter.setDiffComparator(RawTextComparator.DEFAULT)
        diffFormatter.isDetectRenames = true
        val diffs: List<DiffEntry> = diffFormatter.scan(parent.tree, commit.tree)

        for (diff in diffs) {
            val header: FileHeader = diffFormatter.toFileHeader(diff)
            val name = header.newPath //filename with changes
            if (PathInGit != "" && name.startsWith(PathInGit!!)) for (edit in header.toEditList()) {
                if (MapFileNameChanges.containsKey(name)) {
                    MapFileNameChanges[name] = 1
                } else {
                    MapFileNameChanges[name] =  MapFileNameChanges[name]!! + 1
                }
                for (line in edit.endB..edit.beginB) {
                    val key = KeyFilePos(name, line)
                    if (MapFileChanges.containsKey(key)) {
                        MapFileChanges[key] = 1
                    } else {
                        MapFileChanges[key] = MapFileChanges[key]!! + 1
                    }
                }
            }
        }
    }

    fun isCommitInBranch(commit: RevCommit, branchName:String ): Boolean {
        val walk = RevWalk(this.repository)

        val targetCommit: RevCommit = walk.parseCommit(
            repository.resolve(
                commit.name
            )
        )

        return repository.allRefs.entries.find { (key, value) ->
            key.startsWith(Constants.R_HEADS) &&
                    walk.isMergedInto(targetCommit, walk.parseCommit(value.objectId)) &&
                    branchName == value.name
        } != null
    }

    fun getCommits() : Iterable<RevCommit>{
        return if (PathInGit == null)
            git.log().all().call()
        else
            git.log()
                 .add(git.repository.resolve(Constants.HEAD))
                 .addPath(PathInGit).call()
    }

    fun anlyze() {
        val branches = git.branchList().call()

        for (branch in branches) {
            val branchName = branch.name
            val commits = getCommits().filter { commit ->
                Date(commit.commitTime * 1000L).after(StartDate) &&
                        Date(commit.commitTime * 1000L).before(EndDate) &&
                        commit.parentCount > 0
            }

            for (commit in commits) {
                if (isCommitInBranch(commit, branchName)) {
                    val lines = commit.fullMessage.split("\n".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
                    lines.filter { line -> isFixMessage(line) }.map { line -> Matcher.addNewMessage(line) }
                }
                detectChanges(commit.getParent(0), commit)
            }
            Matcher.buildMessageDistances()
        }

        MapFileNameChanges = MapFileNameChanges.sortByDescValue()

        for ((fileName, postion) in MapFileNameChanges.entries) {
            val pairsList =  MapFileChanges.entries.filter {
                    (key,value) -> key.fileName == fileName
            }.map {
                    (key,value) -> Pair(key.position, value)
            }
            pairsList.sortedBy { el -> el.second }
        }
    }

    fun isFixMessage(message:String) : Boolean {
        return "fix" in message
    }
}