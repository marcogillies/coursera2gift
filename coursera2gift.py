import yaml, sys


with open(sys.argv[1], 'r') as stream:  # input file is the first argument
    try:
        yamldata = yaml.load(stream) # parse the yaml file
        outfile = os.path.splitext(sys.argv[1])[0] + ".gift"
        with open(sys.argv[2], 'w') as output:
            # iterate over all of the questions
            for i, d in enumerate(yamldata):
                question = d['variations'][0]
                # format the question prompt, including removing line breaks
                question["prompt"] = question["prompt"].replace("\n", "<br />")
                question["prompt"] = question["prompt"].replace("\r", "<br />")

                # write out the prompt
                # name the questions by number and tag it as html
                output.write("::Q"+str(i+1)+"::[html] " + question['prompt'] + "{" + "\n")

                # this bit checks the number of correct resposnes
                # (for choose all that apply questions)
                numCorrect = 0
                for option in question["options"]:
                    if option["isCorrect"]:
                        numCorrect += 1

                # convert the possible answers
                for option in question["options"]:
                    # remove line breaks in the answer and feedback
                    option["answer"] = option["answer"].replace("\n", " ")
                    option["answer"] = option["answer"].replace("\r", " ")
                    option["feedback"] = option["feedback"].replace("\n", " ")
                    option["feedback"] = option["feedback"].replace("\r", " ")

                    # handle incorrect answers, single correct answers and
                    # multiple correct answers
                    prefix = "~"
                    if option["isCorrect"]:
                        if numCorrect == 1:
                            prefix = "="
                        elif numCorrect > 1:
                            percent = 100/numCorrect
                            prefix = "~%" + str(percent) + "%"

                    # write out the answer
                    output.write(prefix + "[moodle]" + option["answer"] + "#" + option["feedback"] + "\n")

                output.write("}\n\n")
    except yaml.YAMLError as exc:
        print(exc)
