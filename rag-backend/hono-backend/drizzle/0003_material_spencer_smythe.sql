ALTER TABLE "docs" ADD COLUMN "audio_url" text;--> statement-breakpoint
ALTER TABLE "messages" ADD COLUMN "question_id" uuid;--> statement-breakpoint
ALTER TABLE "messages" ADD COLUMN "audio_url" text;--> statement-breakpoint
ALTER TABLE "messages" ADD CONSTRAINT "messages_question_id_messages_id_fk" FOREIGN KEY ("question_id") REFERENCES "public"."messages"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "message_question_id" ON "messages" USING btree ("question_id");