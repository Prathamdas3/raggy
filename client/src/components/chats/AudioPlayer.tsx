export default function AudioPlayer({ src }: { src: string }) {
	if (!src) return null;

	return (
		<div className="space-y-2">
			<audio controls className="w-full">
				<source src={src} type="audio/mpeg" />
				<track kind="captions" srcLang="en" label="English"/>
			</audio>
		</div>
	);
}
