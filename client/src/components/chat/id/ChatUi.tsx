import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";

export default function ChatUI() {
    return <div className="h-full overflow-auto py-2">
        <div className="max-w-5xl mx-auto container">
            <div className="border-t bg-background/95 backdrop-blur">
                <div className="mx-auto max-w-3xl px-4 py-4">
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            // handleSubmit();
                        }}
                        className="relative"
                    >
                        <Textarea
                            // ref={textareaRef}
                            // value={input}
                            // onChange={(e) => setInput(e.target.value)}
                            // onKeyDown={handleKeyDown}
                            // placeholder={
                            // 	isTaskRunning
                            // 		? "Waiting for response…"
                            // 		: "Ask me anything…"
                            // }
                            className="min-h-15 pr-12 resize-none"
                        // disabled={isTaskRunning || isAsking}
                        />

                        <Button
                            type="submit"
                            size="icon"
                            className="absolute right-2 bottom-2 h-8 w-8"
                        // disabled={!input.trim() || isTaskRunning || isAsking}
                        >
                            {/* {isAsking || isTaskRunning ? ( */}
                            {/* <Loader2 className="h-4 w-4 animate-spin" /> */}
                            {/* ) : ( */}
                            <Send className="h-4 w-4" />
                            {/* )} */}
                        </Button>
                    </form>
                </div>
            </div>
        </div>
    </div>
}